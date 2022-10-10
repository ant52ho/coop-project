# clientScript5 is an improved version of clientScript4 with + 1 comms
import time
from os import path
import socket
import subprocess
import os
import redis
import threading
import select
import multiprocessing
import signal
import struct
import fcntl
from createConfs import *
from collectSensorData import *
from projectConf import *

'''Global variables'''
sensorData = []


''' Universal functions '''


def getPartialSubnet(ip):  # ie 20.0.0.5 -> 20.0.0
    return ".".join(ip.split(".")[:3])


def get_ip_linux(interface: str) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    try:
        packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    except OSError as e:
        # print("cannot get IP", e)
        return e
    return socket.inet_ntoa(packed_addr)


def get_ip(iface: str) -> str:
    ip = str(subprocess.check_output(['ifconfig', iface]))
    try:
        ind = ip.index("inet")
        ip = ip[ind + 5: ind + 30]
        ip = ip.split(" ")[0]
        return ip
    except ValueError:
        return 'error'


def ifExists(ifname):
    return path.exists("/sys/class/net/" + str(ifname))


def get_id() -> int:
    if ifExists('br0'):
        ip = get_ip('br0')
        if ip.split(".")[0] == EDGE_ID:
            id = ip.split(".")[-1]
            return int(id)
    ip = get_ip('eth0')  # ie 20.0.0.3
    if ip.split(".")[0] == EDGE_ID:  # ie if [20].0.0.1 == [11].0.0.2
        id = ip.split(".")[-1]
        return int(id)
    return -1


def isIfConnected(ifname):
    retval = False
    f = open("/sys/class/net/" + ifname + "/carrier")
    opened = f.read(1)
    # if there's a physical connection and a dhcp connection hasn't been made yet
    if (opened == "1"):
        retval = True
    else:
        retval = False
        print("interface is not physically connected")
    f.close()
    return retval


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


''' DHCP functions '''


def isDHCPConnected(ifname):
    ipaddr = get_ip(ifname)
    subnet = getPartialSubnet(ipaddr)  # ie. 20.0.0
    edgeSubnet = EDGE_PARTIAL_SUBNET  # ie. 20.0.0

    if (subnet != edgeSubnet):
        return False
    else:
        return True


def connectDHCP():
    os.system('sudo ifconfig eth0 0.0.0.0')
    # this connects the raspi to the DHCP server
    print("Attempting to connect to dhcp")
    os.system('sudo dhclient eth0 -p 1112 -v')

    edgeSubnet = EDGE_PARTIAL_SUBNET  # ie. 20.0.0
    for i in range(15):  # waits up to 30s to acquire + update address
        curAddr = get_ip_linux("eth0")
        brIP = ""
        if ifExists('br0'):
            brIP = get_ip_linux('br0')

        subnet = getPartialSubnet(curAddr)  # ie. 20.0.0
        brSubnet = getPartialSubnet(brIP)
        if subnet == edgeSubnet or brSubnet == edgeSubnet:
            print("Dhcp connected with eth IP", curAddr)
            return True
        print("Connecting to DHCP...")
        time.sleep(2)

    print("Failed to set edge Wifi IP")
    os.system('sudo dhclient -r eth0')
    return False


def configNodeWifi(id, apInterface, clientInterface):
    createDhcpcdConf(id, apInterface)
    createDnsmasqConf(id, apInterface)
    createHostapdConf(id, apInterface)
    createWpaSupplicantConf(id, clientInterface)
    configDefaultHostapd()
    configSysctl()
    restoreIPTables()
    natBetween(apInterface, clientInterface)
    os.system('sudo service hostapd restart')
    os.system('sudo service dnsmasq restart')
    time.sleep(3)


def getDHCPIp():
    while True:
        eth0Exists = ifExists("eth0")
        dhcpConnected = isDHCPConnected("eth0")  # simple IP check

        if (eth0Exists and dhcpConnected == False):
            # make a dhcp connection if eth0 is connected
            if isIfConnected("eth0"):
                dhcpConnected = connectDHCP()

        if dhcpConnected:
            id = get_id()
            if id != -1:
                apInterface = "wlan1"
                clientInterface = "wlan0"
                configNodeWifi(id, apInterface, clientInterface)
        if (dhcpConnected and id != -1):
            return get_ip('eth0')

        time.sleep(3)


''' Bridge functions '''


def makeBridge(id):
    edgeSubnet = EDGE_PARTIAL_SUBNET + ".0/24"  # ie. 20.0.0.0/24
    ipaddr = EDGE_PARTIAL_SUBNET + "." + str(id)
    # if IP address is correct
    print("Bridge IP: " + ipaddr)
    os.system('sudo brctl addbr br0')  # package alraedy installed
    os.system('sudo ifconfig eth1 0.0.0.0')
    os.system('sudo brctl addif br0 eth1')
    os.system('sudo brctl addif br0 eth0')
    os.system('sudo ifconfig br0 up')
    os.system('sudo ifconfig br0 ' + ipaddr)
    # for some reason, eth0 interferes with adding the following route
    os.system('sudo ip addr flush dev eth0')
    os.system('sudo ip route add ' + edgeSubnet +
              ' via ' + ipaddr + ' dev br0')
    print("Bridge made")
    return True


def maintainBridge(id):
    ipaddr = EDGE_PARTIAL_SUBNET + "." + str(id)  # ie 20.0.0.3
    createBridge = True
    while True:
        eth0Exists = ifExists("eth0")
        eth1Exists = ifExists("eth1")
        if (not eth0Exists or not eth1Exists):
            createBridge = True
            os.system("sudo ifconfig eth0 " + ipaddr)
        if (createBridge and eth1Exists and eth0Exists):
            createBridge = not makeBridge(id)
        time.sleep(2)


''' Maintain messaging functions '''


def send(msg, edgeClient):
    try:
        message = msg.encode(FORMAT)
        edgeClient.send(message)
        # 5 second timeout to receive
        res = select.select([edgeClient], [], [], 5)
        if res[0]:
            print(edgeClient.recv(HEADER).decode(FORMAT))
            return True
        else:
            return False
    except Exception as e:
        return False


# sendData reads data from nearby sensors and sends it + status data
def sendData(edgeClient, id, interface):
    # sending status thread
    statusThread = threading.Thread(target=updateStatus, args=(edgeClient, id))
    statusThread.start()

    while True:
        global sensorData
        select = f'f:data:{interface}:' + ','.join(sensorData)
        print(select)
        retval = send(select, edgeClient)
        if not retval:
            break
        # delay before next query
        time.sleep(3)


def updateStatus(edgeClient, id):
    while True:
        isNeighbourConnected = isConnected(
            EDGE_PARTIAL_SUBNET + "." + str(id - 1))
        # f:status:sensor1:status:True
        print('f:status:sensor' + str(id) + ':status:' +
              str(isNeighbourConnected))
        retval = send('f:status:sensor' + str(id) + ':status:' +
                      str(isNeighbourConnected), edgeClient)

        if not retval:
            break
        time.sleep(5)


def startEdgeClient(edgeClient, id, interface):  # should exit if fails
    print("[STARTING] Edge client is starting...")
    retval = send('hello world', edgeClient)
    if not retval:
        return

    # sending data thread
    dataThread = threading.Thread(
        target=sendData, args=(edgeClient, id, interface))
    dataThread.start()
    dataThread.join()


def maintainEthMessaging(id):
    while True:
        try:
            edgeEthClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # edgeClient.setblocking(0)  # to allow timeouts
            edgeEthClient.connect(EDGE_ADDR)
            startEdgeClient(edgeEthClient, id, "eth")
        except Exception as e:
            print('Unable to connect to eth edge socket, error', e)
            time.sleep(3)


def maintainWlanMessaging(id):
    while True:
        try:
            edgeWlanClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # edgeClient.setblocking(0)  # to allow timeouts
            edgeWlanClient.connect(EDGE_WLAN_ADDR)
            startEdgeClient(edgeWlanClient, id, "wlan")
        except Exception as e:
            print('Unable to connect to wlan edge socket, error', e)
            time.sleep(3)


def startupWifi(routerIP):
    # routerIP: 11.0. + str(id - 1) + .1, so 11.0.2.1
    while True:
        os.system("wpa_cli -i wlan0 terminate")
        time.sleep(1)
        os.system(
            "sudo wpa_supplicant -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant-wlan0.conf -B")
        os.system("sudo dhclient wlan0 -v")
        for i in range(15):  # waits up to 30s to acquire + update address
            curAddr = get_ip_linux("wlan0")
            subnet = getPartialSubnet(curAddr)  # ie. 20.0.0
            if subnet == getPartialSubnet(routerIP):
                print("Connected to AP DHCP with ip:", curAddr)
                return True
            print("Connecting to AP DHCP...")
            time.sleep(2)
        print("Failed to connect to AP DHCP, retrying...")


def collectData(id):
    global sensorData
    while True:
        sensorData = collectSensorData(id)
        time.sleep(2.8)


if __name__ == "__main__":
    # refreshing params
    os.system("sudo ip addr flush eth0")
    os.system('sudo ifconfig eth0 0.0.0.0')

    # acquire DHCP connection
    ip = getDHCPIp()
    id = int(ip.split(".")[-1])
    print("Device IP:", ip)
    print("Device ID:", id)

    # wlan conf
    edgeIDPlus1 = str(int(EDGE_ID) + 1)
    routerIP = edgeIDPlus1 + ".0." + str(id - 1) + ".1"
    startupWifi(routerIP)

    # creating a bridge when possible
    bridgeThread = threading.Thread(target=maintainBridge, args=(id, ))
    bridgeThread.start()

    # maintaining eth messaging
    ethMessageThread = threading.Thread(
        target=maintainEthMessaging, args=(id, ))
    ethMessageThread.start()

    # collect data thread
    dataThread = threading.Thread(
        target=collectData, args=(id, ))
    dataThread.start()

    # maintaining wlan messaging
    wlanMessageThread = threading.Thread(
        target=maintainWlanMessaging, args=(id, ))
    wlanMessageThread.start()
