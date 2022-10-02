from projectConf import *
import sqlite3

SQLITE_SUBNET_CONF = f"""
INSERT INTO subnets (
                subnet,
                serial,
                lease_time,
                gateway,
                subnet_mask,
                broadcast_address,
                ntp_servers,
                domain_name_servers,
                domain_name
            ) VALUES (
                '{EDGE_PARTIAL_SUBNET + ".0/24"}',
                0,
                14400,
                '{EDGE_SERVER}',
                '255.255.255.0',
                '{EDGE_PARTIAL_SUBNET + ".255"}',
                NULL,
                NULL,
                NULL
            );
"""

SQLITE_SUBNET_TABLE_CONF = """
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
"""

SQLITE_MAPS_TABLE_CONF_1 = """
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
"""
SQLITE_MAPS_TABLE_CONF_2 = """
-- Case-insensitive MAC-lookups may be handled in-database using either of the following methods:
--  - Put "COLLATE NOCASE" in the column-definition in maps:mac
--  - Include the following index
CREATE INDEX case_insensitive_macs ON maps (mac COLLATE NOCASE);
"""


def initSqlite(sqliteConnection, dbReset):
    try:
        sqliteConnection = sqlite3.connect(
            '/home/pi/dhcp/staticDHCPd/conf/dhcp.sqlite3')
        print("connected to sqlitedb!")
        cursor = sqliteConnection.cursor()
        # some sqlite init commands
        # checks if table exists
        subnetTableExists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='subnets';").fetchall()
        if subnetTableExists == []:
            cursor.execute(SQLITE_SUBNET_TABLE_CONF)

        mapsTableExists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='maps';").fetchall()
        if mapsTableExists == []:
            cursor.execute(SQLITE_MAPS_TABLE_CONF_1)
            cursor.execute(SQLITE_MAPS_TABLE_CONF_2)

        # # ensures only one subnet is possible
        cursor.execute("DELETE FROM subnets")
        # # adds an appropriate subnet to current ip
        cursor.execute(SQLITE_SUBNET_CONF)
        # deletes table records if necessary

        print(cursor.execute("select * from subnets").fetchall())

    except sqlite3.Error as error:
        print(error)
        print("failed to connect to sqlite db")
    finally:
        sqliteConnection.commit()


if __name__ == '__main__':
    try:
        sqliteConnection = sqlite3.connect(
            '/home/pi/dhcp/staticDHCPd/conf/dhcp.sqlite3')
        print("connected to sqlitedb!")
        cursor = sqliteConnection.cursor()
        # some sqlite init commands
        # checks if table exists
        subnetTableExists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='subnets';").fetchall()
        if subnetTableExists == []:
            cursor.execute(SQLITE_SUBNET_TABLE_CONF)

        mapsTableExists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='maps';").fetchall()
        if mapsTableExists == []:
            cursor.execute(SQLITE_MAPS_TABLE_CONF_1)
            cursor.execute(SQLITE_MAPS_TABLE_CONF_2)

        # # ensures only one subnet is possible
        cursor.execute("DELETE FROM subnets")
        # # adds an appropriate subnet to current ip
        cursor.execute(SQLITE_SUBNET_CONF)
        # deletes table records if necessary

        print(cursor.execute("select * from subnets").fetchall())

    except sqlite3.Error as error:
        print(error)
        print("failed to connect to sqlite db")
    finally:
        sqliteConnection.commit()
        sqliteConnection.close()
