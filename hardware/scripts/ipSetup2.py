import os

os.system('sudo ifconfig eth1 10.0.0.12')
os.system('sudo ip route add 10.0.0.10 via 10.0.0.12')
