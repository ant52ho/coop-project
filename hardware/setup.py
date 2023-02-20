# setup for the edge server

import os
# sudo apt-get -y install python3 pip
# note: The revpis come with pip

# sudo pip3 install redis


# curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
# echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
# sudo apt-get update
# sudo apt-get install redis

# sudo apt-get install sqlite3

# set up staticDHCPd
# place dhcp folder here
os.system("cd dhcp")
os.system("install.sh")
os.system("cd ..")

# os.system(sqlite3 dhcp.sqlite3)
# copy and paste:
'''
CREATE TABLE subnets (
    subnet TEXT NOT NULL, -- A human-readable subnet-identifier, typically a CIDR mask.
    serial INTEGER NOT NULL DEFAULT 0, -- A means of allowing a subnet to be reused, just in case you have two 192.168.1.0/24s.
    lease_time INTEGER NOT NULL, -- The number of seconds a "lease" is good for. This can be massive unless properties change often.
    gateway TEXT, -- The IPv4 gateway to supply to clients; may be null.
    subnet_mask TEXT, -- The IPv4 subnet mask to supply to clients; may be null.
    broadcast_address TEXT, -- The IPv4 broadcast address to supply to clients; may be null.
    ntp_servers TEXT, -- A comma-separated list of IPv4 addresses pointing to NTP servers; limit 3; may be null.
    domain_name_servers TEXT, -- A comma-separated list of IPv4 addresses pointing to DNS servers; limit 3; may be null.
    domain_name TEXT, -- The name of the search domain to be provided to clients.
    PRIMARY KEY(subnet, serial)
);

CREATE TABLE maps (
    id,
    mac TEXT PRIMARY KEY NOT NULL, -- The MAC address of the client to whom the IP and associated options will be passed.
    ip TEXT NOT NULL, -- The IPv4 address to provide to the client identified by the associated MAC.
    hostname TEXT, -- The hostname to assign to the client; may be null.
    subnet TEXT NOT NULL, -- A human-readable subnet-identifier, used in conjunction with the serial.
    serial INTEGER NOT NULL DEFAULT 0, -- Together with the serial, this identifies the options to pass to the client.
    UNIQUE (ip, subnet, serial),
    FOREIGN KEY (subnet, serial) REFERENCES subnets (subnet, serial)
);

-- Case-insensitive MAC-lookups may be handled in-database using either of the following methods:
--  - Put "COLLATE NOCASE" in the column-definition in maps:mac
--  - Include the following index
CREATE INDEX case_insensitive_macs ON maps (mac COLLATE NOCASE);
'''


# get bridge utils


# create sqlite database (many sql commands, copy/paste)

# bring over redisTest.conf

# clone redistimeseries, redisjson
# download rust ( it's for redisjson, but we likely won't need it )


'''
Setup for client
'''

# sudo apt update
# sudo apt upgrade
# sudo apt install python3-pip
# sudo pip3 install redis
# pip3 install minimalmodbus
# sudo apt-get install bridge-utils
# sudo apt install dnsmasq
# sudo apt install hostapd
# sudo apt install iptables

'''
Setup for cloud server
'''

# move cloudScript and cloudConf into ec2
# sudo apt update
# sudo apt upgrade
# sudo apt install python3-pip

# curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
# echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
# sudo apt-get update
# sudo apt-get install redis
# git clone --recursive https://github.com/RedisTimeSeries/RedisTimeSeries.git
# cd RedisTimeSeries
# make setup
# make build

# pip3 install --upgrade redis  (because in ubuntu the live redis vesion is 3.5.(something))


# (optional) to check
# from importlib.metadata import version
# version('redis')


# go into ec2 instance and open port 5050 for socket connection
