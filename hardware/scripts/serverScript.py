import redis
import time
import os
import socket
import fcntl
import struct
import subprocess
import sqlite3
from threading import Thread
import threading


# set to true when debugging
dbRESET = True

# set to "" if wanting a dynamic last node
manualLastNode = ""

# this program runs from the server. it detects for disconnections,
# switches modes if a disconnection is detected.


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

# isConnected checks if an individual node is connected


def isConnected(ip):
    try:
        response = subprocess.check_output(
            ['ping', '-c', '1', ip],
            stderr=subprocess.STDOUT,  # get all output
            universal_newlines=True  # return string not bytes
        )
    except subprocess.CalledProcessError:
        response = 'error'

    if response != 'error':
        print(ip + " is up!")
        return True
    else:
        print(ip + " is down!")
        return False

# lastNode calls the database to see which is the currently last node.
# it also returns the last connected node


def lastNode(sqliteConnection):
    if manualLastNode != "":
        return manualLastNode

    max_ip = "10.0.0.1"

    # obtain the last node from the database
    try:
        cursor = sqliteConnection.cursor()
        #id, mac, ip, hostname, subnet, serial

        sqlite_max_query = "SELECT MAX(id) from maps"
        cursor.execute(sqlite_max_query)
        records = cursor.fetchone()
        if records[0] == None:  # if no existing database entries
            return max_ip

        print(records)
        max_id = records[0]
        return '10.0.0.' + str(max_id)

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    return records


def lastConnectedNode(sqliteConnection):
    max_ip = lastNode(sqliteConnection)
    max_id = int(max_ip[7:])

    for i in range(max_id, 0, -1):
        test_ip = "10.0.0." + str(i)
        if isConnected(test_ip):
            return test_ip
    return "10.0.0.1"


# scanNodes scans all nodes and checks if any single is disconnected
def scanNodes(sqliteConnection):
    first = "10.0.0.1"
    last = lastNode(sqliteConnection)
    for node in range(int(first[7:]), int(last[7:]) + 1):
        ip = "10.0.0." + str(node)
        if not isConnected(ip):
            return ip
    return first


# gets the ip address of a certain interface
def get_ip_linux(interface: str) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    try:
        packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    except OSError:
        print("triggered os error")
        return "error"
    return socket.inet_ntoa(packed_addr)

# checks if current device is in ad-hoc mode


def isAdHoc():
    wlanMode = str(subprocess.check_output(['iwconfig', 'wlan0']))
    wlanState = str(subprocess.check_output(['ifconfig', 'wlan0']))
    # print(retval)
    try:
        wlanMode.index("Ad-Hoc")
        wlanState.index("RUNNING")
    except ValueError:
        return False
    return True

# starts the IBSS server
# note: it will error if wpa_supplicant doesn't have p2p_disabled=1


def startIBSS(ip="", channel=4, essid='AHTest'):
    print('starting ibss!')
    if ip == "":
        ip_twin = get_ip_linux("eth0")
        ip = ip_twin[:5] + "1" + ip_twin[6:]
    os.system('sudo ifconfig wlan0 down')
    os.system('sudo iwconfig wlan0 channel ' + str(channel))
    os.system('sudo iwconfig wlan0 mode ad-hoc')
    os.system("sudo iwconfig wlan0 essid '" + essid + "'")
    os.system('sudo ifconfig wlan0 ' + ip)
    os.system('sudo ip addr flush dev wlan0')
    os.system('sudo ip route add 10.0.1.0/24 via ' + ip)
    return True


def restartRedis(conf):
    print("server starting...")
    os.system('sudo redis-server ' + conf)


def startDHCP():
    os.system('sudo python /home/pi/dhcp/staticDHCPd/staticDHCPd')


def deleteTableRecords(sqliteConnection):
    print("db resetting...")
    try:
        cursor = sqliteConnection.cursor()
        #id, mac, ip, hostname, subnet, serial

        truncate_query = "DELETE FROM maps"
        cursor.execute(truncate_query)
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.commit()


def resetRedisKeys():
    r = redis.Redis(host='127.0.0.1', port=6379, password='rat')
    r.flushdb()


def recv(conn, addr):
    msg = conn.recv(HEADER).decode(FORMAT)
    print(f"[{addr}] {msg}")
    conn.send("Msg received".encode(FORMAT))
    return msg


def reply_ip(conn):
    conn.send("10.0.0.1".encode(FORMAT))


def forward(msg, cloudClient):
    send(msg, cloudClient)


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


if __name__ == "__main__":
    print("initiating...")
    os.system('sudo ifconfig eth0 10.0.0.1')
    os.system('sudo ip route add 10.0.0.0/24 via 10.0.0.1')
    os.system('sudo service redis-server stop')

    # initiates the redis server
    redis_thread = Thread(target=restartRedis, args=('redisTest.conf'))
    redis_thread.start()
    time.sleep(3)

    # connects to the redis server
    r = redis.Redis(host='127.0.0.1', port=6379,
                    password='rat', decode_responses=True)
    print(r)
    try:
        r.ping()
    except Exception as e:
        print("unable to connect")

    print(r.get('hello'))

    # starts edgeServer socket and cloudServer socket
    edgeThread = threading.Thread(
        target=startEdgeServer, args=(r))
    cloudThread = threading.Thread(target=maintainCloudClient)
    edgeThread.start()
    cloudThread.start()

    # connects to the sqlite DB
    sqliteConnection = ""
    try:
        sqliteConnection = sqlite3.connect(
            '/home/pi/dhcp/staticDHCPd/dhcp.sqlite3')
    except sqlite3.Error as error:
        print("failed to connect to sqlite db")

    # deletes table records if necessary
    if dbRESET == True:
        deleteTableRecords(sqliteConnection)

    # timer variable for IBSS
    endIBSSTimer = 0

    # initiates the dhcp server
    # the dhcp server will update the redis server as updates are made
    dhcp_thread = Thread(target=startDHCP)
    dhcp_thread.start()

    # logs the current largest connection for client use
    firstNode = '10.0.0.1'
    r.set('firstNode', firstNode)
    r.set('lastNode', lastNode(sqliteConnection))

    # set redis bindings
    r.config_set('bind', '127.0.0.1 10.0.0.1 -::1')

    while True:  # this will become a while loop in the future

        ethConnected = isConnected(lastNode(sqliteConnection))

        if not ethConnected:
            # reset end ibss timer
            endIBSSTimer = 0

            # retval should be used to determine the disconnected node
            retval = scanNodes(sqliteConnection)

            # server raises IBSS based existing ethernet ip
            if not isAdHoc():
                startIBSS(ip="10.0.1.1", channel=4, essid='AHTest')

            # create redis bindings, requires ips to exist
            cmd = r.config_get("bind")
            bindings = cmd['bind']
            if len(bindings.split(' ')) == 3:
                cmd = r.config_set('bind', '127.0.0.1 10.0.0.1 10.0.1.1 -::1')

        if ethConnected:
            # disables IBSS if necessary after waiting for 5 seconds
            if isAdHoc():
                if endIBSSTimer == 0:
                    endIBSSTimer = time.time()
                if time.time() > endIBSSTimer + 5 and endIBSSTimer != 0:
                    print("lower ibss!")
                    os.system('sudo ifconfig wlan0 down')

                    # checks if the right bindings are on redis
                    cmd = r.config_get("bind")
                    bindings = cmd['bind']
                    if len(bindings.split(' ')) != 3:
                        cmd = r.config_set('bind', '127.0.0.1 10.0.0.1 -::1')

                    endIBSSTimer = 0

        time.sleep(3)

    sqliteConnection.close()  # this may error, because not on same level as above
    redis_thread.join()
    dhcp_thread.join()
