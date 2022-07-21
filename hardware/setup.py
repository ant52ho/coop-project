# setup for the edge server

import os
# sudo apt-get -y install python3 pip
# note: The revpis come with pip

# sudo pip3 install redis

# sudo apt-get install redis

# sudo apt-get install sqlite3

# set up staticDHCPd
# place dhcp folder here
os.system("cd dhcp")
os.system("install.sh")
os.system("cd ..")


# get bridge utils


# create sqlite database (many sql commands, copy/paste)

# bring over redisTest.conf
