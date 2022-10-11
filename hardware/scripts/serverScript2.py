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
from sqlite3Conf import *

dbRESET = True

'''Global variables'''
cloudClientGlobal = None
nodeRec = {}  # records last node data
ethAllConnected = True  # determines if eth is all connected

'''helper functions'''


def get_ip_linux(interface: str) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    try:
        packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    except OSError as e:
        # print("cannot get IP", e)
        return e
    return socket.inet_ntoa(packed_addr)


def configEdgeEth():
    os.system('sudo ifconfig eth0 ' + EDGE_SERVER)
    os.system('sudo ip route add ' + EDGE_PARTIAL_SUBNET +
              '.0/24 via ' + EDGE_SERVER)
    curAddr = get_ip_linux("eth0")
    print(f"Edge Eth IP set at {curAddr}")
    return


def configEdgeWifi(apInterface, clientInterface):
    edgeId = EDGE_SERVER.split(".")[-1]
    ipID = str(int(EDGE_SERVER.split(".")[0]) + 1)  # ie 21
    createDhcpcdConf(edgeId, apInterface)
    createDnsmasqConf(edgeId, apInterface)
    createHostapdConf(edgeId, apInterface)
    configDefaultHostapd()
    configSysctl()
    restoreIPTables()
    natBetween(apInterface, clientInterface)
    os.system('sudo service hostapd restart')
    os.system('sudo service dnsmasq restart')
    # waits for a max. of 20 seconds for the wifi name to configure
    correctAddr = f"{ipID}.0.{edgeId}.1"
    for i in range(20):
        curAddr = get_ip_linux("wlan1")
        if curAddr == correctAddr:
            print("Edge Wifi IP set at", curAddr)
            return True
        print("Setting edge Wifi IP...")
        time.sleep(2)
    print("Failed to set edge Wifi IP")
    return False


def restartRedis(conf):
    print("Restarting Redis Server!")
    os.system('sudo service redis-server stop')
    print("Redis restarted!")
    os.system('sudo redis-server ' + conf)


def initSqlite(sqliteConnection):
    try:
        sqliteConnection = sqlite3.connect(SQLITE_PATH)
        print("connected to sqlitedb!")
        cursor = sqliteConnection.cursor()
        # some sqlite init commands
        # checks if table exists
        subnetTableExists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='subnets';").fetchall()
        if subnetTableExists == []:
            cursor.execute(SQLITE_SUBNET_TABLE_CONF)

        mapsTableExists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='maps';").fetchall()
        if mapsTableExists == []:
            cursor.execute(SQLITE_MAPS_TABLE_CONF_1)
            cursor.execute(SQLITE_MAPS_TABLE_CONF_2)

        # # ensures only one subnet is possible
        cursor.execute("DELETE FROM subnets")
        # # adds an appropriate subnet to current ip
        cursor.execute(SQLITE_SUBNET_CONF)
        # deletes table records if necessary

    except sqlite3.Error as error:
        print("SQLITE3 ERROR!:", error)
        print("failed to connect to sqlite db")
    finally:
        sqliteConnection.commit()


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


def send(msg, cloudClient):
    try:
        message = msg.encode(FORMAT)
        cloudClient.send(message)
        print(cloudClient.recv(HEADER).decode(FORMAT))
        return True
    except Exception as e:
        print("Error in sending message! Try starting the cloud server?")
        return False


def startCloudClient(cloudClient):
    print("[STARTING] Cloud client is starting...")
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
            startCloudClient(cloudClient)  # updates status of sensor1
        except ConnectionRefusedError or OSError:
            time.sleep(3)
            print('Unable to connect to cloud server!, retrying...')
        # print('loop')


def recv(conn, addr):
    try:
        msg = conn.recv(HEADER).decode(FORMAT)
        if not msg:
            return
        print(f"[{addr}] {msg}")
        conn.send("Msg received".encode(FORMAT))
        return msg
    except Exception as e:
        print("Error in receiving message!", e)
        return False


def forward(msg, cloudClient):
    global ethAllConnected
    global nodeRec
    # f:data:eth:2,1665377260,None,None,None,0.0,None,None,None,None,None,None,None,None
    # f:status:sensor2:status:True

    # note: sometimes sockets may receive incomplete strings. This leads to
    #   inconsistencies when indexing strings received from sockets, so
    #   so prevent this indexing issue it must be wrapped in a try/except
    try:
        interpret = msg.split(":")
        cmd = interpret[1]
        print(cmd)

        if cmd == "data":
            payload = interpret[3].split(",")
            id = payload[0]
            time = payload[1]
            source = interpret[2]

            if ethAllConnected and source == "eth":
                send(msg, cloudClient)
                nodeRec[id] = time

            if not ethAllConnected:
                if id in nodeRec:
                    if nodeRec[id] != time:
                        send(msg, cloudClient)
                        nodeRec[id] = time
                else:
                    send(msg, cloudClient)
                    nodeRec[id] = time
        elif cmd == "status":
            send(msg, cloudClient)
    except Exception as e:
        print("Failed to send forward message to Cloud!:", e)
        return


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        msg = recv(conn, addr)
        if not msg:
            break
        if len(msg) >= 2 and msg[:2] == 'f:':
            forward(msg, cloudClientGlobal)
    conn.close()


def startEthEdgeServer():
    ethEdgeServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ethEdgeServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ethEdgeServer.bind(EDGE_ADDR)
    print("[STARTING] Edge eth server is starting...")
    ethEdgeServer.listen()
    print(f"[LISTENING] Edge eth server is listening on {EDGE_SERVER}")
    while True:
        conn, addr = ethEdgeServer.accept()
        thread = threading.Thread(
            target=handle_client, args=(conn, addr))
        thread.start()


def startWlanEdgeServer():
    wlanEdgeServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    wlanEdgeServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    wlanEdgeServer.bind(EDGE_WLAN_ADDR)
    print("[STARTING] Edge wlan server is starting...")
    wlanEdgeServer.listen()
    print(f"[LISTENING] Edge wlan server is listening on {EDGE_WLAN_SERVER}")
    while True:
        conn, addr = wlanEdgeServer.accept()
        thread = threading.Thread(
            target=handle_client, args=(conn, addr))
        thread.start()


def startDHCP():
    os.system(f'sudo python {DHCP_PATH}')


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


def checkConnectivity():
    # initiates sqlite connection
    sqliteConnection = ""
    try:
        sqliteConnection = sqlite3.connect(SQLITE_PATH)
        initSqlite(sqliteConnection)
        if dbRESET == True:
            deleteTableRecords(sqliteConnection)
        print("Connected to SQLite!")
    except sqlite3.Error as error:
        print("SQLITE3 ERROR", error)

    global ethAllConnected
    while True:
        ethAllConnected = isConnected(lastNode(sqliteConnection))
        print("ethAllConnected", ethAllConnected)
        time.sleep(3)


if __name__ == '__main__':
    apInterface = 'wlan1'
    clientInterface = 'eth1'
    redis_thread = Thread(target=restartRedis, args=(REDIS_EDGE_PATH,))
    redis_thread.start()

    configEdgeEth()
    configEdgeWifi(apInterface, clientInterface)

    # connects to the redis server
    r = redis.Redis(host='127.0.0.1', port=6379,
                    password='rat', decode_responses=True)
    print("Connected to Redis!")

    print(r)
    try:
        r.ping()
    except Exception as e:
        print("unable to connect to redis")

    print(r.get('hello'))

    # initiates sqlite connection

    sqliteConnection = ""
    try:
        sqliteConnection = sqlite3.connect(SQLITE_PATH)
        initSqlite(sqliteConnection)
        if dbRESET == True:
            deleteTableRecords(sqliteConnection)
        print("Connected to SQLite!")
    except sqlite3.Error as error:
        print("SQLITE3 ERROR", error)

    # logs the current largest connection for client use
    firstNode = EDGE_SERVER
    r.set('firstNode', firstNode)
    r.set('lastNode', lastNode(sqliteConnection))

    # set redis bindings
    r.config_set('bind', '127.0.0.1 ' + EDGE_SERVER + ' -::1')

    cloudThread = threading.Thread(target=maintainCloudClient)
    cloudThread.start()

    ethEdgeThread = threading.Thread(
        target=startEthEdgeServer)
    ethEdgeThread.start()

    wlanEdgeThread = threading.Thread(
        target=startWlanEdgeServer)
    wlanEdgeThread.start()

    # initiates the dhcp server
    dhcp_thread = Thread(target=startDHCP)
    dhcp_thread.start()

    connectivity_thread = Thread(
        target=checkConnectivity)
    connectivity_thread.start()
