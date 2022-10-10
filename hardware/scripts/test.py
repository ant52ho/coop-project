from projectConf import *
from createConfs import *
import os
import time
import socket
import struct
import fcntl


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


configEdgeEth()
