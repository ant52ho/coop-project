# this script constantly runs while in the cloud. It maintains the
#   socket connection and handles database entries and querying

import socket
import threading
import redis
import os
import time
import threading as Thread

# user defined constants:
HEADER = 128  # strings should just be this long, right
PORT = 5050  # this port will have to change for edge server
#SERVER = socket.gethostbyname(socket.gethostname())
SERVER = '172.31.40.10'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)


def resetRedisKeys():
    r = redis.Redis(host='127.0.0.1', port=6379, password='rat')
    r.flushdb()


def restartRedis(conf):
    print("server starting...")
    os.system('sudo redis-server ' + conf)


# recv() receives a message and returns a basic reply


def recv(conn, addr):
    msg = conn.recv(HEADER).decode(FORMAT)
    print(f"[{addr}] {msg}")
    conn.send("Msg received".encode(FORMAT))
    return msg


def reply_ip(conn):
    conn.send("10.0.0.1".encode(FORMAT))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        msg = recv(conn, addr)

        if msg == DISCONNECT_MESSAGE:
            break

        # add additional functions here

        elif msg == 'get_ip':
            ip = reply_ip(conn)

        elif len(msg) >= 2 and msg[:2] == 'f:':
            print('received forwarded message')
            handleForwardedMessage(msg)

    conn.close()


def handleForwardedMessage(msg):
    # assuming message format is
    # ie day-temp-temp-wind-precip
    # ie f:2013-12-21-74-60-2-31
    return True


def start():
    # initiates the redis server
    redis_thread = Thread(target=restartRedis, args=("redisCloud.conf"))
    redis_thread.start()
    time.sleep(3)

    # connects to the redis server
    r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

    # initializes socket server
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == '__main__':
    print("[STARTING] server is starting...")
    start()
