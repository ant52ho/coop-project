import logging
import sqlite3
import redis


# Copy this file to one of the following locations, then rename it to conf.py:
# /etc/staticDHCPd/, ./conf/

# For a full overview of what these parameters mean, and to further customise
# your system, please consult the configuration and scripting guides in the
# standard documentation


# Whether to daemonise on startup (you don't want this during initial setup)
DAEMON = False

# WARNING: The default UID and GID are those of root. THIS IS NOT GOOD!
# If testing, set them to your id, which you can find using `id` in a terminal.
# If going into production, if no standard exists in your environment, use the
# values of "nobody": `id nobody`
# The UID this server will use after initial setup
UID = 0
# The GID this server will use after initial setup
GID = 0

# The IP of the interface to use for DHCP traffic
DHCP_SERVER_IP = '10.0.0.1'

# The database-engine to use
# For details, see the configuration guide in the documentation.
DATABASE_ENGINE = 'SQLite'

SQLITE_FILE = '/home/pi/dhcp/staticDHCPd/conf/dhcp.sqlite3'

# Server behaviour
ALLOW_LOCAL_DHCP = True

ALLOW_DHCP_RELAYS = True

AUTHORITATIVE = True

DHCP_SERVER_PORT = 1111
DHCP_CLIENT_PORT = 1112

# Scripts

# the first address that will be allocated (2-255)
# ie if 10.0.0.2, then put 2
SECOND_ID = 2

# this function connects the unknown mac to the dhcp server


def filterPacket(packet, method, mac, client_ip, relay_ip, port):
    if method == "DISCOVER":
        try:
            # connect to sqlite db
            sqliteConnection = sqlite3.connect(
                '/home/pi/dhcp/staticDHCPd/conf/dhcp.sqlite3')
            cursor = sqliteConnection.cursor()
            print("connected to SQLite")

            # selects the largest element by id
            sqlite_max_query = "SELECT MAX(id) from maps"
            cursor.execute(sqlite_max_query)
            records = cursor.fetchone()

            # decides on the next id based on current max id, and
            #   inserts it into the table
            id = 0
            if records[0] == None:  # if no existing database entries
                id = SECOND_ID
            else:
                id = int(records[0]) + 1
            ip = "10.0.0." + str(id)
            addDevice = 'INSERT INTO maps (id, mac, ip, hostname, subnet, serial) VALUES (' + str(
                id) + ', "' + str(mac) + '", "' + ip + '", ' + 'NULL, "10.0.0.0/24", 0);'
            print(addDevice)
            cursor.execute(addDevice)

            # insert the largest value into redis
            r = redis.Redis(host='127.0.0.1', port=6379, password='rat')
            r.set('lastNode', ip)

            #cursor.execute("select * from maps")
            #records = cursor.fetchall()
            # print(records)
            # cursor.close()

        except sqlite3.Error as error:
            print("Failed to read data from sqlite table", error)
        finally:
            if sqliteConnection:
                sqliteConnection.commit()
                sqliteConnection.close()
                print("The SQLite connection is closed")
    print(method)
    return True
