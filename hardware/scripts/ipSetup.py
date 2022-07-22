# this program sets up the ip address for the edge server.
# it can be used for a headless setup, where you blindly type
# "python ipSetup.py" and then ssh to 10.0.0.1 from your eth connected
# computer


import os

os.system('sudo ifconfig eth0 10.0.0.1')
os.system('sudo ip route add 10.0.0.0/24 via 10.0.0.1')
os.system('sudo ifconfig eth1 10.0.0.11')
os.system('sudo ip route add 10.0.0.10 via 10.0.0.11')
