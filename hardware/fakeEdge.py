# this program tests if it's possible to be both a client and server
#   code used in this file will eventually be added to serverScript.
# Note: the cloud server must be up for the program to run
import socket
import threading
import time

# common constants
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# Cloud constants
CLOUD_PORT = 5050  # this port will have to change for edge server
CLOUD_SERVER = "18.117.112.0"
CLOUD_ADDR = (CLOUD_SERVER, CLOUD_PORT)

# Edge constants
EDGE_PORT = 5060
EDGE_SERVER = socket.gethostbyname(socket.gethostname())
#EDGE_SERVER = '10.0.0.1'
EDGE_ADDR = (EDGE_SERVER, EDGE_PORT)

# global variable
cloudClientGlobal = None


# recv() receives a message and returns a basic reply


def recv(conn, addr):
    msg = conn.recv(HEADER).decode(FORMAT)
    print(f"[{addr}] {msg}")
    conn.send("Msg received".encode(FORMAT))
    return msg


def reply_ip(conn):
    conn.send("10.0.0.1".encode(FORMAT))


def forward(msg, cloudClient):
    try:
        send(msg, cloudClient)
    except Exception as e:  # attribute error, connectionAbortedError
        print("unable to forward message")
        return False
    return True


def tempStore(r, cmd):
    r.rpush('temp', cmd)


def emptyTempStore(r, cloudClient):
    while r.exists('temp'):
        retval = r.lpop('temp')
        forward(retval, cloudClient)

    return True


def handle_client(conn, addr, redisConnection):
    print(f"[NEW CONNECTION] {addr} connected.")
    redisEmpty = True

    while True:
        msg = recv(conn, addr)

        if msg == DISCONNECT_MESSAGE:
            break

        elif msg == 'get_ip':
            ip = reply_ip(conn)

        elif len(msg) >= 2 and msg[:2] == 'f:':
            retval = forward(msg, cloudClientGlobal)
            if not retval:
                tempStore(redisConnection, msg)
                redisEmpty = False
            if retval and not redisEmpty:
                redisEmpty = emptyTempStore(redisConnection, cloudClientGlobal)

    conn.close()

# send() sends a message, and recieves an acknowledgement. This function should
#   composed together with other functions, similar to get_ip()


def send(msg, cloudClient):
    message = msg.encode(FORMAT)
    cloudClient.send(message)
    print(cloudClient.recv(HEADER).decode(FORMAT))


# to implement a new function, have the function send a string and receive a reply
def get_ip(cloudClient):
    send('get_ip')
    return cloudClient.recv(HEADER).decode(FORMAT)


def startEdgeServer(redisConnection):
    edgeServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    edgeServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    edgeServer.bind(EDGE_ADDR)
    print("[STARTING] Edge server is starting...")
    edgeServer.listen()
    print(f"[LISTENING] Edge server is listening on {EDGE_SERVER}")
    while True:
        conn, addr = edgeServer.accept()
        thread = threading.Thread(
            target=handle_client, args=(conn, addr, redisConnection))
        thread.start()

        # this line might be inaccurate when using both at once
        print(f"[ACTIVE EDGE CONNECTIONS] {threading.active_count() - 1}")


def startCloudClient(cloudClient):
    print("[STARTING] Cloud client is starting...")

    send('hello world', cloudClient)

    while True:
        try:
            msg = input()
            if msg == 'aah' or msg == DISCONNECT_MESSAGE:
                send(DISCONNECT_MESSAGE)
                break
            elif msg == 'get_ip':
                ip = get_ip(cloudClient)
                print(ip)
            else:
                send(msg, cloudClient)
        except Exception as e:
            print("disconnected from cloud server")
            break


def maintainCloudClient():
    while True:
        try:
            cloudClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cloudClient.connect(CLOUD_ADDR)
            global cloudClientGlobal
            cloudClientGlobal = cloudClient
            startCloudClient(cloudClient)
        except ConnectionRefusedError:
            time.sleep(3)
        print('loop')


if __name__ == '__main__':
    redisConnection = 'redis connection'
    edgeThread = threading.Thread(
        target=startEdgeServer, args=(redisConnection))
    cloudThread = threading.Thread(target=maintainCloudClient)
    edgeThread.start()
    cloudThread.start()
    edgeThread.join()
    cloudThread.join()
