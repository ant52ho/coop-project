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
print("hello world")
'''
#import this
import redis
import os
#import sqlite3
from os import path
import socket
import fcntl
import struct
import subprocess
import sqlite3
import time
# works only for linux
# check if there's a physical ethernet connection using path 
# /sys/class/net/eth0/carrier (1 is connected)
# note: if adapter cable is not plugged in, sys/class/net/eth1 will not exist
#if cable is connected, run the dhcp start command
#after receiving an IP address, wait until an eth1 interface exists
#once it exists, create a bridge

def get_ip(iface: str) -> str:
    ip = str(subprocess.check_output(['ifconfig', iface]))
    try:
        ind = ip.index("inet")
        ip = ip[ind + 5 : ind + 30]
        ip = ip.split(" ")[0]
        return ip
    except ValueError:
        return 'error'

def package_installed(pck): #need to test if it works
    devnull = open(os.devnull,"w")
    retval = subprocess.call(["dpkg","-s",pck],stdout=devnull,stderr=subprocess.STDOUT)
    devnull.close()
    if retval != 0:
        print("Package ", pck, " is not installed.")
        return False
    else:
        return True

def makeBridge():
    ipaddr = get_ip("eth0")
        #if IP address is correct 
    if (ipaddr[:6] == "10.0.0"):
        print("assigned ip address: " + ipaddr)
        os.system('sudo brctl addbr br0') #package alraedy installed 
        os.system('sudo ifconfig eth1 0.0.0.0')
        os.system('sudo brctl addif br0 eth1')
        os.system('sudo brctl addif br0 eth0')
        os.system('sudo ifconfig br0 up')
        os.system('sudo ifconfig br0 ' + ipaddr)
        os.system('sudo ip addr flush dev eth0') # for some reason, eth0 interferes with adding the following route
        os.system('sudo ip route add 10.0.0.0/24 via ' + ipaddr + ' dev br0')
      
        return True
    else: 
        return False

def connectDHCP():
    print("attempting to connect to dhcp")
    os.system('sudo dhclient eth0 -v') # this connects the raspi to the DHCP server
    ipaddr = get_ip("eth0")
    print("current ip addr: " , ipaddr)
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
  
    #if there's a physical connection and a dhcp connection hasn't been made yet
    if (opened == "1"): 
        retval = True
    else:
        retval = False
        print("interface is not physically connected")
    f.close()
  
    return retval


dhcpConnected = False
createBridge = True

while True:
    eth0Exists = ifExists("eth0")
    #eth1Exists = ifExists("eth1")
    eth1Exists = False
    if isIfConnected("eth0"):
        dhcpConnected = connectDHCP()
    
    if dhcpConnected:
        print("dhcp is now connected")
    
    print(dhcpConnected, eth0Exists, eth1Exists, createBridge)
    time.sleep(3)



dhcpConnected = False
createBridge = True

while True:
    eth0Exists = ifExists("eth0")
    #eth1Exists = ifExists("eth1")
    eth1Exists = False

    # bridge must be reinstalled eventually if neither interface exists
    # note: It shouldn't be immediately reinstalled, because both interfaces must 
    #     first exist
    if (not eth0Exists or not eth1Exists):
        createBridge = True

    dhcpConnected = isDHCPConnected("eth0") # a simple check if it has the right IP
    
    if (eth0Exists and dhcpConnected == False):
    
    # make a dhcp connection if eth0 is connected
        if isIfConnected("eth0"):
            dhcpConnected = connectDHCP()
    
    if dhcpConnected:
        print("dhcp is now connected")
    
    print(dhcpConnected, eth0Exists, eth1Exists, createBridge)

    
    #if a dhcp connection exists and a bridge hasn't been made
    if (dhcpConnected and eth1Exists and eth0Exists and createBridge):
        # if bridge package is installed
        if (package_installed("bridge-utils")):
            createBridge = makeBridge()
            createBridge = False
            print("bridge made")
        else: 
            print("bridge utils not installed")
            break
    
    time.sleep(3)
    
'''