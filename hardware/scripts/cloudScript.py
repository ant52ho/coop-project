# this script constantly runs while in the cloud. It maintains the
#   socket connection and handles database entries and querying

import socket
import threading

# user defined constants:
HEADER = 128  # strings should just be this long, right
PORT = 5050  # this port will have to change for edge server
#SERVER = socket.gethostbyname(socket.gethostname())
SERVER = '18.117.112.0'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

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

    conn.close()


def start():
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
