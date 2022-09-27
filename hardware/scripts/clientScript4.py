# clientScript4 is an improved version of clientScript3 with better readability.
# it should also provide some perfomance improvements and some bug fixes

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
from createConfs import *
from collectSensorData import *
from projectConf import *

''' for sensor communication '''
import minimalmodbus
import serial

# common constants
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# Edge constants
EDGE_PORT = 5060
#EDGE_SERVER = socket.gethostbyname(socket.gethostname())
EDGE_SERVER = '20.0.0.1'
EDGE_PARTIAL_SUBNET = ".".join(EDGE_SERVER.split(".")[:3])  # ie 20.0.0
# ie 20, or 192. Note: incomplete subnet, cheap id
EDGE_ID = EDGE_SERVER.split(".")[0]
EDGE_ADDR = (EDGE_SERVER, EDGE_PORT)


''' Universal functions '''


def getPartialSubnet(ip):  # ie 20.0.0.5 -> 20.0.0
    return ".".join(ip.split(".")[:3])


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

# isIfConnected() determines if there's an actual device connected to if
#   note: a single ended eth connection does not count
#   note: the interface solely existing does not count


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
    time.sleep(3)  # waiting for the ip to update
    ipaddr = get_ip("eth0")
    subnet = getPartialSubnet(ipaddr)  # ie. 20.0.0
    edgeSubnet = EDGE_PARTIAL_SUBNET  # ie. 20.0.0
    print("current ip addr: ", ipaddr)
    if (subnet == edgeSubnet):
        print("dhcp connected")
        return True
    else:
        os.system('sudo dhclient -r eth0')
        return False


def getDHCPIp():
    while True:
        eth0Exists = ifExists("eth0")
        dhcpConnected = isDHCPConnected("eth0")  # simple IP check

        if (eth0Exists and dhcpConnected == False):

            # make a dhcp connection if eth0 is connected
            if isIfConnected("eth0"):
                dhcpConnected = connectDHCP()

        # creates a dhcpcd file, a dnsmasq.conf file, hostapd.conf file
        if dhcpConnected:
            id = get_id()
            if id != -1:
                # these four conf files are necessary
                createDhcpcdConf(id)
                createDnsmasqConf(id)
                createHostapdConf(id)
                createWpaSupplicantConf(id)

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


''' Maintain Connectivity functions '''


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


def getEdge(r):
    retval = None
    try:
        retval = r.ping()
    except Exception as e:
        print("unable to connect to redis server")
        return EDGE_SERVER

    retval = r.get('lastNode')
    return str(retval)


def isWifi():  # make this only run if wlan1 exists
    wlan1Mode = ""
    wlan1State = ""
    if ifExists("eth1"):
        wlan1Mode = str(subprocess.check_output(['iwconfig', 'wlan1']))
        wlan1State = str(subprocess.check_output(['ifconfig', 'wlan1']))
    wlan0State = str(subprocess.check_output(['ifconfig', 'wlan0']))
    try:
        if ifExists("eth1"):
            wlan1Mode.index("APTest")
            wlan1State.index("RUNNING")
        wlan0State.index("RUNNING")
    except ValueError:
        return False
    return True


def isRoutedtoAP(routerIP):
    routed = str(subprocess.check_output(
        ['route', '-n']).decode("utf-8")).split("\n")
    for line in routed:
        if line == "":
            continue
        route = line.split()
        if route[-1] == 'wlan0' and route[0] == EDGE_SERVER and route[1] == routerIP:
            return True
    return False

# a one time wifi startup


def startupWifi(routerIP):
    # routerIP: 11.0. + str(id - 1) + .1, so 11.0.2.1
    # needs testing
    while True:
        os.system("wpa_cli -i wlan0 terminate")
        time.sleep(1)
        os.system(
            "sudo wpa_supplicant -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant-wlan0.conf -B")
        os.system("sudo dhclient wlan0 -v")
        time.sleep(2)  # waiting for the ip to update
        ip = get_ip("wlan0")
        if getPartialSubnet(ip) == getPartialSubnet(routerIP):
            print('connected to AP dhcp')
            return


def startWifi():
    if ifExists("eth1"):
        os.system("sudo service hostapd start")
        os.system("sudo service dnsmasq start")
    return True


def stopWifi():
    if ifExists("eth1"):
        os.system("sudo service hostapd stop")
        os.system("sudo service dnsmasq stop")
    return True


def routeToWifi(routerIP):
    print("adding route:", routerIP, "to " + EDGE_SERVER)
    os.system('sudo ip route add ' + EDGE_SERVER +
              ' via ' + routerIP + ' dev wlan0')


def routeToCord(routerIP):
    print("deleting route:", routerIP, "to " + EDGE_SERVER)
    os.system('sudo ip route del ' + EDGE_SERVER +
              ' via ' + routerIP + ' dev wlan0')

    # a new bridge will have to be created
    if (ifExists("eth1") and ifExists("eth0")):
        makeBridge(id)
    return True


def redisEth(r):
    return r.ping()


def ethAllConnected():
    r = redis.Redis(host=EDGE_SERVER, port=6379,
                    password='rat', decode_responses=True)
    if isConnected(EDGE_SERVER):
        retval = r.get("ethAllConnected")
        if retval == "True":
            return True
        return False
    else:
        return False


def maintainConnectivity(id):
    timerStart = 0  # timer
    # ie if edge is 20.0.0.1, then edgeIDPlus1 = 21
    edgeIDPlus1 = str(int(EDGE_ID) + 1)
    routerIP = edgeIDPlus1 + ".0." + str(id - 1) + ".1"

    # this line will have to guarentee that it is connected to dhcp,
    # and can ping an adjacent node via wifi.
    # maybe it sometimes can't connect to dhcp because the eth route is preventing it?
    startupWifi(routerIP)

    while True:
        # below is accurate because on AP mode, [EDGE_SERVER] can't ping "forwards"
        #   because of specific port forwarding
        ethConnected = ethAllConnected()
        print("ethAllConnected:", ethConnected)

        routedToAP = isRoutedtoAP(routerIP)

        # if not ethConnected and not isWifi():

        if not ethConnected and not routedToAP:
            print("starting AP/C!")
            # startWifi()
            routeToWifi(routerIP)
            # reset possible counter
            timerStart = 0

        # if ethConnected and isWifi():
        if ethConnected and routedToAP:
            if timerStart == 0:
                timerStart = time.time()
            if time.time() > timerStart + 5 and timerStart != 0:
                print("stopping AP/C!")
                # stopWifi()
                routeToCord(routerIP)
                timerStart = 0

        time.sleep(3)


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


# sendData reads data from nearby sensors and sends it
def sendData(edgeClient, id):
    while True:
        retArr = collectSensorData(id)
        select = 'f:data:' + ','.join(retArr)
        print(select)
        retval = send(select, edgeClient)
        # if server doesn't respond
        if not retval:
            print("failed to send to edge!")
            time.sleep(3)  # timeout for connection
        # delay before next query
        time.sleep(3)


# readRegister reads a sensor register and returns a dict object with error and
#   value
def readRegister(instrument, address, decimals, code):
    retval = {}
    try:
        # read_register(registeraddress: int, number_of_decimals: int = 0,
        #   functioncode: int = 3, signed: bool = False)
        retval["value"] = instrument.read_register(address, decimals, code)
        retval["error"] = False
    except Exception as e:
        print(e)
        retval["value"] = e
        retval["error"] = True
    return retval


def sendFakeData(entries, edgeClient, id, all=False):

    # indices of interesting data
    dayIndex = 0
    tempHighIndex = 1
    tempLowIndex = 2
    windHighIndex = 15
    precipitationIndex = 18

    f = open("austin_weather.csv", "r")
    line = f.readline().split(',')
    heading = [str(id), line[dayIndex], line[tempHighIndex], line[tempLowIndex],
               line[windHighIndex], line[precipitationIndex]]
    print(heading)

    count = 0
    while True:
        if count == entries and all == False:
            break

        line = f.readline().split(',')
        # print(line)
        select = [str(id), line[dayIndex], line[tempHighIndex], line[tempLowIndex],
                  line[windHighIndex], line[precipitationIndex]]
        print(select)

        # data format: f:data:id,val,val,val...
        select = 'f:data:' + ','.join(select)

        retval = send(select, edgeClient)

        # if server doesn't respond
        if not retval:
            f.close()
            break

        time.sleep(1)  # for debugging
        count += 1
    f.close()
    return True


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


def startEdgeClient(edgeClient, id):  # should exit if fails
    print("[STARTING] Edge client is starting...")
    retval = send('hello world', edgeClient)

    if not retval:
        return

    # sending status thread
    statusThread = threading.Thread(target=updateStatus, args=(edgeClient, id))
    statusThread.start()

    # sending data thread
    dataThread = threading.Thread(
        target=sendData, args=(edgeClient, id))

    # sending fake data thread (for testing)
    # dataThread = threading.Thread(
    #     target=sendFakeData, args=(10, edgeClient, id, True))

    dataThread.start()

    statusThread.join()
    dataThread.join()


def maintainMessaging(id):
    while True:
        try:
            edgeClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # edgeClient.setblocking(0)  # to allow timeouts
            edgeClient.connect(EDGE_ADDR)
            startEdgeClient(edgeClient, id)
        except Exception as e:
            print('unable to connect to edge socket, error', e)
            time.sleep(3)


if __name__ == "__main__":

    # refreshing params
    os.system("sudo ip addr flush eth0")
    os.system('sudo ifconfig eth0 0.0.0.0')

    # acquire DHCP connection
    ip = getDHCPIp()
    id = int(ip[7:])
    print("Device IP:", ip)
    print("Device ID:", id)

    # creating a bridge when possible
    bridgeThread = threading.Thread(target=maintainBridge, args=(id, ))
    bridgeThread.start()

    # maintaining connectivity
    connectivityThread = threading.Thread(
        target=maintainConnectivity, args=(id, ))
    connectivityThread.start()

    # maintaining messaging
    messageThread = threading.Thread(target=maintainMessaging, args=(id, ))
    messageThread.start()

    bridgeThread.join()
    connectivityThread.join()
    messageThread.join()
