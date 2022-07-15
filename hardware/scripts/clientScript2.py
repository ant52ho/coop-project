import time
import os
import socket
import fcntl
import struct
import subprocess
import redis

STATICLAST = False

# this program is the script that is ran on the client side. 

# getEdge gets the edge node
def getEdge(r):
    if STATICLAST:
        return STATICLAST
    
    retval = False
    
    try:
        retval = r.ping()
    except Exception as e:
        print("unable to connect")
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

# startIBSS starts the IBSS server
def startIBSS(ip = "", channel=4, essid='AHTest'):
    if ip == "":
        ip_twin = get_ip_linux("eth0")
        ip = ip_twin[:5] + "1" + ip_twin[6:]
    os.system('sudo ifconfig wlan0 down')
    os.system('sudo iwconfig wlan0 channel ' + str(channel))
    os.system('sudo iwconfig wlan0 mode ad-hoc')
    os.system("sudo iwconfig wlan0 essid '" + essid + "'")
    os.system('sudo ifconfig wlan0 ' + ip)
    # need to add route, test
    return True

# checks if current device is in ad-hoc mode. Requires both wlan to be up and
#   running in adhoc mode
def isAdHoc():
    wlanMode = str(subprocess.check_output(['iwconfig', 'wlan0']))
    wlanState = str(subprocess.check_output(['ifconfig', 'wlan0']))
    #print(retval)
    try:
        wlanMode.index("Ad-Hoc")
        wlanState.index("RUNNING")
    except ValueError:
        return False
    return True

if __name__ == '__main__':

    timerStart = 0 # timer
    
    r = redis.Redis(host='10.0.0.1', port=6379, password='rat', decode_responses=True)

    # we will assume it is already ethernet connected

    while True: #this will be replaced with a while loop

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
