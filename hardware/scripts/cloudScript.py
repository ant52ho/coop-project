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

# key retention duration in redis
RETENTION = 3600000  # retention in milliseconds

# DATAFORMAT is the format which data is inputted from clientScript
# note: could make dataformat into a dict for alternative naming
DATAFORMAT = ["id", "day", "val1", "val2", "val3", "val4"]


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

        unixTime = int(data[1])

        commands = DATAFORMAT

        for commandIndex in range(2, len(commands)):

            if data[commandIndex] == "None":
                continue

            newKey = id + ":" + commands[commandIndex]
            if not r.exists(newKey):
                r.ts().create(newKey)

            print("\n", newKey, unixTime,
                  data[commandIndex])

            r.ts().add(key=newKey, timestamp=unixTime,
                       value=data[commandIndex], retention_msecs=RETENTION, duplicate_policy='last')
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
