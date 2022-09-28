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
from projectConf import *
from createConfs import *


# set to true when debugging
dbRESET = True

# this program runs from the server. it detects for disconnections,
# switches modes if a disconnection is detected.

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
    max_ip = EDGE_SERVER

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
        return EDGE_PARTIAL_SUBNET + "." + str(max_id)

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    return records


def lastConnectedNode(sqliteConnection):
    max_ip = lastNode(sqliteConnection)
    max_id = int(max_ip.split(".")[-1])

    for i in range(max_id, 0, -1):
        test_ip = EDGE_PARTIAL_SUBNET + "." + str(i)
        if isConnected(test_ip):
            return test_ip
    return EDGE_SERVER


# scanNodes scans all nodes and checks if any single is disconnected
def scanNodes(sqliteConnection):
    first = EDGE_SERVER
    last = lastNode(sqliteConnection)
    for node in range(int(first.split(".")[-1]), int(last.split(".")[-1]) + 1):
        ip = EDGE_PARTIAL_SUBNET + "." + str(node)
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


def isAP():
    wlanMode = str(subprocess.check_output(['iwconfig', 'wlan1']))
    wlanState = str(subprocess.check_output(['ifconfig', 'wlan1']))
    # print(retval)
    try:
        wlanMode.index("APTest")
        wlanState.index("RUNNING")
    except ValueError:
        return False
    return True


def startAP():
    os.system("sudo service hostapd start")
    os.system("sudo service dnsmasq start")
    return True


def stopAP():
    os.system("sudo service hostapd stop")
    os.system("sudo service dnsmasq stop")
    return True

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
    if not msg:
        return
    print(f"[{addr}] {msg}")
    conn.send("Msg received".encode(FORMAT))
    return msg


def forward(msg, cloudClient):
    return send(msg, cloudClient)


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

        if not msg:
            break

        if msg == DISCONNECT_MESSAGE:
            break

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
    try:
        message = msg.encode(FORMAT)
        cloudClient.send(message)
        print(cloudClient.recv(HEADER).decode(FORMAT))
        return True
    # except AttributeError:  # cloud client isn't connected
    except Exception as e:
        print(e)
        return False


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

        # this line is inaccurate, use math to make it accurate cause constant scaling
        print(f"[ACTIVE EDGE CONNECTIONS] {threading.active_count() - 1}")


def startCloudClient(cloudClient):
    print("[STARTING] Cloud client is starting...")

    send('hello world', cloudClient)

    while True:
        print('f:status:sensor1:status:True')
        retval = send('f:status:sensor1:status:True', cloudClient)

        if not retval:
            break

        time.sleep(3)


def maintainCloudClient():
    while True:
        try:
            cloudClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cloudClient.connect(CLOUD_PUBLIC_ADDR)
            global cloudClientGlobal
            cloudClientGlobal = cloudClient
            startCloudClient(cloudClient)
        except ConnectionRefusedError or OSError:
            time.sleep(3)
            print('not connected to cloud server, retrying...')
        print('loop')


if __name__ == "__main__":
    print("initiating...")
    os.system('sudo ifconfig eth0 ' + EDGE_SERVER)
    os.system('sudo ip route add ' + EDGE_PARTIAL_SUBNET +
              '.0/24 via ' + EDGE_SERVER)
    os.system('sudo service redis-server stop')

    # initiates the redis server
    redis_thread = Thread(target=restartRedis, args=('redisTest.conf',))
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

    # configures the hotspot files
    edgeId = EDGE_SERVER.split(".")[-1]
    createDhcpcdConf(edgeId)
    createDnsmasqConf(edgeId)
    createHostapdConf(edgeId)
    configDefaultHostapd()
    configSysctl()
    restoreIPTables()
    # nat between
    apIf = 'wlan1'
    clientIf = 'eth0'
    natBetween(apIf, clientIf)

    # starts edgeServer socket and cloudServer socket
    edgeThread = threading.Thread(
        target=startEdgeServer, args=(r,))
    cloudThread = threading.Thread(target=maintainCloudClient)
    edgeThread.start()
    cloudThread.start()

    # connects to the sqlite DB
    sqliteConnection = ""
    try:
        sqliteConnection = sqlite3.connect(
            '/home/pi/dhcp/staticDHCPd/conf/dhcp.sqlite3')
        cursor = sqliteConnection.cursor()
        print("connected to sqlitedb!")
    except sqlite3.Error as error:
        print("failed to connect to sqlite db")

    # deletes table records if necessary
    if dbRESET == True:
        deleteTableRecords(sqliteConnection)

    # timer variable for IBSS
    endAPTimer = 0

    # initiates the dhcp server
    # the dhcp server will update the redis server as updates are made
    dhcp_thread = Thread(target=startDHCP)
    dhcp_thread.start()

    # logs the current largest connection for client use
    firstNode = EDGE_SERVER
    r.set('firstNode', firstNode)
    r.set('lastNode', lastNode(sqliteConnection))

    # set redis bindings
    r.config_set('bind', '127.0.0.1 ' + EDGE_SERVER + ' -::1')

    while True:  # this will become a while loop in the future
        ethConnected = isConnected(lastNode(sqliteConnection))
        print("ethAllConnected", ethConnected)
        print("loop")
        r.set("ethAllConnected", str(ethConnected))

        if not ethConnected and not isAP():
            # reset end ibss timer
            endAPTimer = 0
            print("starting AP!")
            startAP()

        if ethConnected and isAP():
            if endAPTimer == 0:
                endAPTimer = time.time()
            if time.time() > endAPTimer + 5 and endAPTimer != 0:
                print("stopping AP!")
                stopAP()
            endAPTimer = 0

        time.sleep(3)

    sqliteConnection.close()  # this may error, because not on same level as above
    redis_thread.join()
    dhcp_thread.join()
