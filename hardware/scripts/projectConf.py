'''
This file is a file of constants.
Modifying the constants will change the nature of the program
'''

'''The below constant MUST be the as in the dhcp server's conf.py'''
EDGE_SERVER = '20.0.0.1'
'''Take extra care to remember the above ^'''

'''cloudscript constants'''

'''serverScript constants'''

# common constants
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# Cloud constants
CLOUD_PORT = 5050  # this port will have to change for edge server
CLOUD_SERVER = "3.15.28.149"
CLOUD_ADDR = (CLOUD_SERVER, CLOUD_PORT)

# Edge constants
EDGE_PORT = 5060
#EDGE_SERVER = socket.gethostbyname(socket.gethostname())
EDGE_SERVER = '20.0.0.1'
EDGE_PARTIAL_SUBNET = ".".join(EDGE_SERVER.split(".")[:3])  # ie 20.0.0
# ie 20, or 192. Note: incomplete subnet, cheap id
EDGE_ID = EDGE_SERVER.split(".")[0]
EDGE_ADDR = (EDGE_SERVER, EDGE_PORT)


'''clientscript constants'''
# common constants
HEADER = 128
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# Edge constants
EDGE_PORT = 5060
#EDGE_SERVER = socket.gethostbyname(socket.gethostname())
EDGE_SERVER = '20.0.0.1'
EDGE_PARTIAL_SUBNET = ".".join(EDGE_SERVER.split(".")[:3])  # ie 20.0.0
# ie 20, or 192. Note: incomplete subnet, cheap id
EDGE_ID = EDGE_SERVER.split(".")[0]
EDGE_ADDR = (EDGE_SERVER, EDGE_PORT)


'''sensor data formatting'''
# DATAFORMAT is the format which data is inputted from clientScript
#   DATAFORMAT must be consistent across both programs
# note: could make dataformat into a dict for alternative naming
# ie: sensor2:val1
# should change to an dictionary that matches to index ie: 1: "id"
DATAFORMAT = ["id", "time", "h2", "isobutylene", "ammonia", "propane",
              "chlorine", "vis", "co", "temperature", "humidity",
              "no", "no2", "nox"]

DATAINDICES = {
    0: "id",
    1: "time",
    2: "h2",
    3: "isobutylene",
    4: "ammonia",
    5: "propane",
    6: "chlorine",
    7: "vis",
    8: "co",
    9: "temperature",
    10: "humidity",
    11: "no",
    12: "no2",
    13: "nox",
}

SENSORS = DATAFORMAT[2:]

# constants for chart formatting, must be consistent with dataformat
DATAUNITS = {
    "h2": "LEL%",
    "isobutylene": "ppm",
    "ammonia": "ppm",
    "propane": "LEL%",
    "chlorine": "ppm",
    "vis": "%",
    "co": "ppm",
    "temperature": "°C",
    "humidity": "%",
    "no": "ppm",
    "no2": "ppm",
    "nox": "ppm",
}

DATALABELS = {
    "h2": "H2",
    "isobutylene": "Isobutylene",
    "ammonia": "NH3",
    "propane": "C3H8",
    "chlorine": "Cl2",
    "vis": "Opacity",
    "co": "CO",
    "temperature": "Temperature",
    "humidity": "Humidity",
    "no": "NO",
    "no2": "NO2",
    "nox": "NOX",
}

# bounds of the data
#   formatted in [min, max]
#   use [0,0] if bounds are auto
DATABOUNDS = {
    "h2": [0, 100],
    "isobutylene": [0, 100],
    "ammonia": [0, 100],
    "propane": [0, 100],
    "chlorine": [0, 20],
    "vis": [0, 100],
    "co": [0, 300],
    "temperature": [-40, 100],
    "humidity": [0, 100],
    "no": [0, 100],
    "no2": [0, 10],
    "nox": [0, 100],
}

# this constant does nothing. It should only help as a notepad to
#   track modbus slave setup
SLAVEIDS = {
    1: "h2",
    2: "isobutylene",
    3: "ammonia",
    4: "propane",
    5: "chlorine",
    6: "viconox",
}
