'''
import redis

r = redis.Redis(host='127.0.0.1', port=6379, password='rat')

cmd = r.config_get("bind")
print(r.config_get("bind"))
bindings = cmd['bind']
if len(bindings.split(' ')) != 3:
    cmd = r.config_set('bind', '127.0.0.1 10.0.0.1 -::1')
    print("successfully changed: ", r.config_get("bind"))


'''

import socket

print("start")

# common constants
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


def send(msg, cloudClient):
    try:
        message = msg.encode(FORMAT)
        cloudClient.send(message)
        print(cloudClient.recv(HEADER).decode(FORMAT))
        return True
    except AttributeError:  # cloud client isn't connected
        return False


# Cloud constants
CLOUD_PORT = 5050  # this port will have to change for edge server
CLOUD_SERVER = "18.219.10.248"
CLOUD_ADDR = (CLOUD_SERVER, CLOUD_PORT)

cloudClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cloudClient.connect(CLOUD_ADDR)

print("[STARTING] Cloud client is starting...")

send('hello world', cloudClient)
