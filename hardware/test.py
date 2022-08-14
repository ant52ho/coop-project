# today's task: ensure that redis works when threaded,
# have a correct implementation of redis querying within maintainConnection


import time
from os import path
import socket
import subprocess
import os
import redis
import threading
import select


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
        return '10.0.0.1'

    retval = r.get('lastNode')
    return str(retval)


def isAP():
    wlanMode = str(subprocess.check_output(['iwconfig', 'wlan1']))
    wlanState = str(subprocess.check_output(['ifconfig', 'wlan1']))
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


def routeToAP():
    os.system('sudo ifconfig br0 down')
    os.system('sudo ifconfig eth0 down')
    return True


def routeToCord():
    os.system("sudo ifconfig eth0 up")
    os.system("sudo ifconfig br0 up")

    # a new bridge will have to be created
    if (ifExists("eth1") and ifExists("eth0")):
        makeBridge(id)
    return True


def redisEth(r):
    return r.ping()


def ethAllConnected(r):
    if isConnected('10.0.0.1'):
        retval = r.get("ethAllConnected")
        print("retval", retval)
        if retval == "True":
            return True
        return False
    else:
        return False


def maintainConnectivity():
    r = redis.Redis(host='10.0.0.1', port=6379,
                    password='rat', decode_responses=True)
    timerStart = 0  # timer
    stopAP()  # for routing purposes

    while True:
        # below is accurate because on AP mode, 10.0.0.1 can't ping "forwards"
        #   because of specific port forwarding
        print("checking redis")
        ethConnected = ethAllConnected(r)
        print("ethAllConnected:", ethConnected)

        if not ethConnected and not isAP():
            print("starting AP/C!")
            startAP()
            routeToAP()
            # reset possible counter
            timerStart = 0

        if ethConnected and isAP():
            if timerStart == 0:
                timerStart = time.time()
            if time.time() > timerStart + 5 and timerStart != 0:
                stopAP()
                routeToCord()
                print("stopping AP!")
                timerStart = 0

        time.sleep(3)


def forever():
    while True:
        print("hello")
        time.sleep(10)


if __name__ == "__main__":

    # maintaining connectivity
    connectivityThread = threading.Thread(target=maintainConnectivity)
    connectivityThread.start()

    randomThread = threading.Thread(target=forever())
    randomThread.start()
    randomThread.join
