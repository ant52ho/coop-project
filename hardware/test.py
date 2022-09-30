import subprocess
import fileinput
import sys

EDGE_SERVER = '20.0.0.1'
EDGE_PARTIAL_SUBNET = ".".join(EDGE_SERVER.split(".")[:3])  # ie 20.0.0
# ie 20, or 192. Note: incomplete subnet, cheap id
EDGE_ID = EDGE_SERVER.split(".")[0]


# this function deletes existing subnets from sqlite3 db and creates a new one
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
print(SQLITE_SUBNET_CONF)
