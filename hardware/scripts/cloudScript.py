# this script constantly runs while in the cloud. It maintains the
#   socket connection and handles database entries and querying

import socket
from threading import Thread
import redis
import os
import time
import datetime
from projectConf import *


def resetRedisKeys():
    r = redis.Redis(host='127.0.0.1', port=6379, password='rat')
    r.flushdb()


def restartRedis(conf):
    print("Cloud server starting...")
    os.system('killall redis-server ')
    os.system('sudo redis-server ' + conf)


# recv() receives a message and returns a basic reply


def recv(conn, addr):
    msg = conn.recv(HEADER).decode(FORMAT)
    print(f"[{addr}] {msg}")
    conn.send("Msg received".encode(FORMAT))
    return msg


def reply_ip(conn):
    conn.send(EDGE_SERVER.encode(FORMAT))


def handle_client(conn, addr, r):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        msg = recv(conn, addr)

        if msg == DISCONNECT_MESSAGE:
            break

        # add additional functions here

        elif len(msg) >= 2 and msg[:2] == 'f:':
            print('received forwarded message')
            inputData(msg, r)

    conn.close()


def inputData(msg, r):
    # sometimes incomplete strings might be sent. this is why everything will be
    #  kept inside a try/except block

    try:
        # based off of clientScript4.py updateStatus, keep in serverScript
        if msg.split(":")[1] == "status":
            msg = msg.split(":")

            statusDict = {
                "True": "up",
                "False": "down",
            }

            msg[-1] = statusDict[msg[-1]]

            cmdKey = (':').join(msg[2:4])
            cmdValue = msg[-1]

            r.set(cmdKey, cmdValue)
            return True

        # based on clientScript4.py sendData
        if msg.split(":")[1] == "data":
            # f:data:source:id,val,val,val...
            data = msg.split(":")[-1].split(',')
            id = 'sensor' + str(data[0])
            # unit dependent on clientScript4, keep at "s"

            # since the indv. raspi time may be inaccurate, we use the clock
            # of the cloud server, which must be synced.
            # in other words, the timestamp serves only as an ID.
            unixTime = int(time.time())
            print(unixTime)

            # commands = DATAFORMAT
            commands = DATAINDICES

            # print(data)
            if len(data) != len(DATAFORMAT):
                print("wrong data format! data not stored", data)
                return False

            for commandIndex in range(2, len(commands)):

                # if sensor doesn't have data
                if data[commandIndex] == "None":
                    continue

                # 1 key for "all", one key for "averaged"
                newKey = id + ":" + commands[commandIndex]
                newKeyAll = id + ":" + commands[commandIndex] + ":all"

                # creating aggregation key, and all key
                if not r.exists(newKey):
                    r.ts().create(newKey, retention_msecs=RETENTIONCOMPACT)
                    print(
                        f"Created new compacted keyset {newKey} lasting {RETENTIONCOMPACT} secs!")

                if not r.exists(newKeyAll):
                    r.ts().create(newKeyAll, retention_msecs=RETENTIONALL)
                    print(
                        f"Created new keyset {newKeyAll} lasting {RETENTIONALL} secs!")

                # creating the aggregation rule
                try:
                    r.ts().createrule(newKeyAll, newKey, "avg", BUCKET)
                    print(
                        f"Created new aggregation rule to move keys from {newKeyAll} to {newKey} in {BUCKET}s buckets")
                except redis.exceptions.ResponseError:
                    pass

                r.ts().add(key=newKeyAll, timestamp=unixTime,
                           value=data[commandIndex], retention_msecs=RETENTIONALL, duplicate_policy='last')
            return True
    except Exception as e:
        print(e)
        pass


def start():
    # os.system('sudo service redis-server stop')
    redis_thread = Thread(target=restartRedis, args=(REDIS_CLOUD_PATH,))
    redis_thread.start()
    time.sleep(5)

    # connects to the redis server
    r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

    # stores data constants into redis
    r.set("sensors", ",".join(SENSORS))

    for key in DATAUNITS:  # ie val1:unit -> unit1
        r.set(key + ":unit", DATAUNITS[key])

    for key in DATALABELS:  # ie val1:label -> label1
        r.set(key + ":label", DATALABELS[key])

    for key in DATABOUNDS:  # ie val1:min -> 0, val1:max -> 0
        r.set(key + ":min", DATABOUNDS[key][0])
        r.set(key + ":max", DATABOUNDS[key][1])

    # initializes socket server
    server.listen()
    print(f"[LISTENING] Server is listening on {CLOUD_PUBLIC_SERVER}")
    while True:
        conn, addr = server.accept()
        thread = Thread(target=handle_client, args=(conn, addr, r))
        thread.start()


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(CLOUD_PRIVATE_ADDR)
    print("[STARTING] server is starting...")
    start()
