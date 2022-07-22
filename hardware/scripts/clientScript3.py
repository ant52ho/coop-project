import time
import os.path
from os import path
import socket
import fcntl
import struct
import subprocess
import os
import redis
import threading


# common constants
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# Edge constants
EDGE_PORT = 5060
#EDGE_SERVER = socket.gethostbyname(socket.gethostname())
EDGE_SERVER = '10.0.0.1'
EDGE_ADDR = (EDGE_SERVER, EDGE_PORT)


def get_ip(iface: str) -> str:
    ip = str(subprocess.check_output(['ifconfig', iface]))
    try:
        ind = ip.index("inet")
        ip = ip[ind + 5: ind + 30]
        ip = ip.split(" ")[0]
        return ip
    except ValueError:
        return 'error'


def get_id() -> int:
    ip = get_ip('br0')
    if ip[:2] == "10":
        id = ip[7:]
        print(id)
        return int(id)

    ip = get_ip('eth0')  # ie 10.0.0.3
    if ip[:2] == "10":
        id = ip[7:]
        print(id)
        return int(id)


def package_installed(pck):  # need to test if it works
    devnull = open(os.devnull, "w")
    retval = subprocess.call(
        ["dpkg", "-s", pck], stdout=devnull, stderr=subprocess.STDOUT)
    devnull.close()
    if retval != 0:
        print("Package ", pck, " is not installed.")
        return False
    else:
        return True


def makeBridge():
    ipaddr = get_ip("eth0")
    # if IP address is correct
    if (ipaddr[:6] == "10.0.0"):
        print("assigned ip address: " + ipaddr)
        os.system('sudo brctl addbr br0')  # package alraedy installed
        os.system('sudo ifconfig eth1 0.0.0.0')
        os.system('sudo brctl addif br0 eth1')
        os.system('sudo brctl addif br0 eth0')
        os.system('sudo ifconfig br0 up')
        os.system('sudo ifconfig br0 ' + ipaddr)
        # for some reason, eth0 interferes with adding the following route
        os.system('sudo ip addr flush dev eth0')
        os.system('sudo ip route add 10.0.0.0/24 via ' + ipaddr + ' dev br0')

        return True
    else:
        return False


def connectDHCP():
    print("attempting to connect to dhcp")
    os.system('sudo ifconfig eth0 0.0.0.0')
    # this connects the raspi to the DHCP server
    os.system('sudo dhclient eth0 -v')
    ipaddr = get_ip("eth0")
    print("current ip addr: ", ipaddr)
    if (ipaddr[:6] == "10.0.0"):
        print("dhcp connected")
        return True
    else:
        os.system('sudo dhclient -r eth0')
        return False

# ifExists() checks if a certain interface exists


def ifExists(ifname):
    return path.exists("/sys/class/net/" + str(ifname))

# isDHCPConnected() checks if a certain node is configured to dhcp


def isDHCPConnected(ifname):
    ipaddr = get_ip(ifname)
    if (ipaddr[:6] != "10.0.0"):
        return False
    else:
        return True

# isIfConnected(ifname) checks if interface ifname has a physical connection to
#   another device


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

# getEdge gets the edge node
# uses the redis object, r.


def getEdge(r):
    if STATICLAST:
        return STATICLAST

    retval = False

    try:
        retval = r.ping()
    except Exception as e:
        print("unable to connect to redis server")
        return '10.0.0.1'

    retval = r.get('lastNode')
    return str(retval)


# isConnected checks if a node can ping another node.
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

# startIBSS starts the IBSS server


def startIBSS(ip="", channel=4, essid='AHTest'):
    if ip == "":
        ip_twin = get_ip("eth0")
        ip = ip_twin[:5] + "1" + ip_twin[6:]
    os.system('sudo ifconfig wlan0 down')
    os.system('sudo iwconfig wlan0 channel ' + str(channel))
    os.system('sudo iwconfig wlan0 mode ad-hoc')
    os.system("sudo iwconfig wlan0 essid '" + essid + "'")
    os.system('sudo ifconfig wlan0 ' + ip)
    os.system('sudo ip addr flush dev wlan0')
    os.system('sudo ip route add 10.0.1.0/24 via ' + ip)
    return True

# checks if current device is in ad-hoc mode. Requires both wlan to be up and
#   running in adhoc mode


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


def send(msg, edgeClient):
    message = msg.encode(FORMAT)
    edgeClient.send(message)
    print(edgeClient.recv(HEADER).decode(FORMAT))


def startEdgeClient(edgeClient):
    print("[STARTING] Edge client is starting...")

    send('hello world', edgeClient)

    sendData(10, edgeClient, all=True)

    # while True:
    #     try:
    #         msg = input()
    #         if msg == 'aah' or msg == DISCONNECT_MESSAGE:
    #             send(DISCONNECT_MESSAGfE)
    #             break
    #         elif msg == 'get_ip':
    #             ip = get_ip(edgeClient)
    #             print(ip)
    #         else:
    #             send(msg, edgeClient)
    #     except Exception as e:
    #         print("disconnected from cloud server")
    #         break


def maintainEdgeClient():
    while True:
        try:
            edgeClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            edgeClient.connect(EDGE_ADDR)
            startEdgeClient(edgeClient)
        except ConnectionRefusedError:
            time.sleep(3)
        print('loop')


# this program mimicks sending data


def sendData(entries, edgeClient, all=False):

    # indices of interesting data
    dayIndex = 0
    tempHighIndex = 1
    tempLowIndex = 2
    windHighIndex = 15
    precipitationIndex = 18

    id = get_id()

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
        select = 'f:' + ','.join(select)
        send(select, edgeClient)
        time.sleep(1)  # for debugging
        count += 1
    return True


if __name__ == "__main__":

    STATICLAST = False

    dhcpConnected = False

    createBridge = True

    ethOnceConnected = False

    timerStart = 0  # timer

    os.system("sudo ifconfig eth0 0.0.0.0")

    r = redis.Redis(host='10.0.0.1', port=6379,
                    password='rat', decode_responses=True)

    edgeThread = threading.Thread(target=maintainEdgeClient)
    edgeThread.start()

    while True:
        eth0Exists = ifExists("eth0")
        eth1Exists = ifExists("eth1")
        #eth1Exists = False

        # bridge must be reinstalled eventually if neither interface exists
        # note: It shouldn't be immediately reinstalled, because both interfaces must
        #     first exist
        if (not eth0Exists or not eth1Exists):
            createBridge = True

        # a simple check if it has the right IP
        dhcpConnected = isDHCPConnected("eth0")

        if (eth0Exists and dhcpConnected == False):

            # make a dhcp connection if eth0 is connected
            if isIfConnected("eth0"):
                dhcpConnected = connectDHCP()

        print(dhcpConnected, eth0Exists, eth1Exists, createBridge)

        # if a dhcp connection exists and a bridge hasn't been made
        if (dhcpConnected and eth1Exists and eth0Exists and createBridge):
            # if bridge package is installed
            if (package_installed("bridge-utils")):
                createBridge = makeBridge()
                createBridge = False
                print("bridge made")
            else:
                print("bridge utils not installed")
                break

        if not ethOnceConnected and isConnected('10.0.0.1'):
            print("eth connected!")
            ethOnceConnected = True

        if ethOnceConnected:

            # the entire system is connected if the node can ping both both edges
            ethConnected = isConnected('10.0.0.1') and isConnected(getEdge(r))

            # if eth edges cannot be pinged
            if not ethConnected:

                # if ad-hoc is currently off
                if not isAdHoc():
                    print("raising ibss!")
                    retval = startIBSS(ip="", channel=4, essid='AHTest')

                # reset possible counter
                timerStart = 0

            if ethConnected:
                # if adhoc is on but ethernet connections are detected
                if isAdHoc():
                    # the program will wait for 5 seconds before disabling IBSS mode
                    if timerStart == 0:
                        timerStart = time.time()
                    if time.time() > timerStart + 5 and timerStart != 0:
                        os.system('sudo ifconfig wlan0 down')
                        print("lower ibss!")
                        timerStart = 0

        time.sleep(3)
