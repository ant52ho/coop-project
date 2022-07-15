# this program tests if it's possible to be both a client and server
#   code used in this file will eventually be added to serverScript.
# Note: the cloud server must be up for the program to run

import socket
import threading

# common constants
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# Cloud constants
CLOUD_PORT = 5050  # this port will have to change for edge server
CLOUD_SERVER = "18.117.112.0"
CLOUD_ADDR = (CLOUD_SERVER, CLOUD_PORT)
cloudClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cloudClient.connect(CLOUD_ADDR)

# Edge constants
EDGE_PORT = 5060
EDGE_SERVER = socket.gethostbyname(socket.gethostname())
#EDGE_SERVER = '10.0.0.1'
SERVER_ADDR = (EDGE_SERVER, EDGE_PORT)
edgeServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
edgeServer.bind(SERVER_ADDR)

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

        elif msg == 'get_ip':
            ip = reply_ip(conn)

    conn.close()

# send() sends a message, and recieves an acknowledgement. This function should
#   composed together with other functions, similar to get_ip()


def send(msg):
    message = msg.encode(FORMAT)
    cloudClient.send(message)
    print(cloudClient.recv(HEADER).decode(FORMAT))


# to implement a new function, have the function send a string and receive a reply
def get_ip():
    send('get_ip')
    return cloudClient.recv(HEADER).decode(FORMAT)


def startEdgeServer():
    print("[STARTING] Edge server is starting...")
    edgeServer.listen()
    print(f"[LISTENING] Edge server is listening on {EDGE_SERVER}")
    while True:
        conn, addr = edgeServer.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        # this line might be inaccurate when using both at once
        print(f"[ACTIVE EDGE CONNECTIONS] {threading.active_count() - 1}")


def startCloudClient():
    print("[STARTING] Cloud client is starting...")

    send('hello world')

    while True:
        msg = input()
        if msg == 'aah' or msg == DISCONNECT_MESSAGE:
            send(DISCONNECT_MESSAGE)
            break
        elif msg == 'get_ip':
            ip = get_ip()
            print(ip)
        else:
            send(msg)


if __name__ == '__main__':
    edgeThread = threading.Thread(target=startEdgeServer)
    cloudThread = threading.Thread(target=startCloudClient)
    edgeThread.start()
    cloudThread.start()
