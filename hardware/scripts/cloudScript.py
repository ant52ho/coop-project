# this script constantly runs while in the cloud. It maintains the
#   socket connection and handles database entries and querying

import socket
import threading
import redis
import os
import time
import datetime

# user defined constants:
HEADER = 128  # strings should just be this long, right
PORT = 5050  # this port will have to change for edge server
#SERVER = socket.gethostbyname(socket.gethostname())
SERVER = '172.31.41.126'  # must be private ip address
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# bucket retention in redis (s)
BUCKET = 3600

# all key retention duration in redis
RETENTIONALL = BUCKET * 2 * 1000  # retention in milliseconds

RETENTIONCOMPACT = 0  # in ms


# DATAFORMAT is the format which data is inputted from clientScript
#   DATAFORMAT must be consistent across both programs
# note: could make dataformat into a dict for alternative naming
# ie: sensor2:val1
DATAFORMAT = ["id", "day", "val1", "val2", "val3", "val4"]

SENSORS = DATAFORMAT[2:]

# constants for chart formatting, must be consistent with dataformat
DATAUNITS = {
    "val1": "unit1",
    "val2": "unit2",
    "val3": "unit3",
    "val4": "unit4",
}

DATALABELS = {
    "val1": "label1",
    "val2": "label2",
    "val3": "label3",
    "val4": "label4",
}

# bounds of the data
#   formatted in [min, max]
#   use [0,0] if bounds are auto
DATABOUNDS = {
    "val1": [0, 0],
    "val2": [0, 0],
    "val3": [0, 0],
    "val4": [0, 0],
}


def resetRedisKeys():
    r = redis.Redis(host='127.0.0.1', port=6379, password='rat')
    r.flushdb()


def restartRedis(conf):
    print("server starting...")
    os.system('killall redis-server ' + conf)
    os.system('sudo redis-server ' + conf)


# recv() receives a message and returns a basic reply


def recv(conn, addr):
    msg = conn.recv(HEADER).decode(FORMAT)
    print(f"[{addr}] {msg}")
    conn.send("Msg received".encode(FORMAT))
    return msg


def reply_ip(conn):
    conn.send("10.0.0.1".encode(FORMAT))


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

    # based off of clientScript4.py updateStatus
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
        # f:data:id,val,val,val...
        data = msg.split(":")[-1].split(',')
        # data = msg[2:].split(',')

        id = 'sensor' + str(data[0])
        # day = data[1]

        # unixTime = int(time.mktime(
        #     datetime.datetime.strptime(day, "%Y-%m-%d").timetuple()))

        # commands =  ["id", "day", "tempHigh", "tempLow", "wind", "rain"]

        unixTime = int(data[1])  # unit dependent on clientScript4, keep at "s"

        commands = DATAFORMAT

        for commandIndex in range(2, len(commands)):

            # if sensor doesn't have data
            if data[commandIndex] == "None":
                continue

            # 1 key for all, one key for bucketed
            newKey = id + ":" + commands[commandIndex]
            newKeyAll = id + ":" + commands[commandIndex] + ":all"

            # creating aggregation key, and all key
            if not r.exists(newKey):
                r.ts().create(newKey, retention_msecs=RETENTIONCOMPACT)

            if not r.exists(newKeyAll):
                r.ts().create(newKeyAll)

            # creating the aggregation rule
            try:
                r.ts().createrule(newKeyAll, newKey, "avg", BUCKET)
            except redis.exceptions.ResponseError:
                pass

            r.ts().add(key=newKeyAll, timestamp=unixTime,
                       value=data[commandIndex], retention_msecs=RETENTIONALL, duplicate_policy='last')
        print("stored in redis!")
        return True


def start():
    # os.system('sudo service redis-server stop')

    # # initiates the redis server
    # redis_thread = threading.Thread(
    #     target=restartRedis, args=("redisCloud.conf",))
    # redis_thread.start()
    # time.sleep(3)

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
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, r))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ADDR)
    print("[STARTING] server is starting...")
    start()
