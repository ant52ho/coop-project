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
import os
import socket
import struct
import fcntl


def get_ip_linux(interface: str) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    try:
        packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    except OSError:
        print("triggered os error")
        return "error"
    return socket.inet_ntoa(packed_addr)


def startIBSS(ip="", channel=4, essid='AHTest'):
    print('starting ibss!')
    if ip == "":
        ip_twin = get_ip_linux("eth0")
        ip = ip_twin[:5] + "1" + ip_twin[6:]
    os.system('sudo ifconfig wlan0 up')
    # os.system('sudo iwconfig wlan0 channel ' + str(channel)) # impossible on some pis
    #os.system('sudo iwconfig wlan0 mode ad-hoc')
    #os.system("sudo iwconfig wlan0 essid '" + essid + "'")
    os.system('sudo ifconfig wlan0 ' + ip)
    #os.system('sudo ip addr flush dev wlan0')
    os.system('sudo ip route add 10.0.1.0/24 via ' + ip)
    return True


startIBSS()
