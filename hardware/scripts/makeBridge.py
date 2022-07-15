import os
import os.path
from os import path
import socket
import fcntl
import struct

def get_ip_linux(interface: str) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    return socket.inet_ntoa(packed_addr)

def makeBridge():
  ipaddr = get_ip_linux("eth0")
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
    print("bridge made")
    return True
  else: 
    return False

if __name__ == "__main__":
  makeBridge()