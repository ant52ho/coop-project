import minimalmodbus
import serial
import time

'''This section should be copy/pasted to match cloudScript.py and collectSensorData.py'''

# DATAFORMAT is the format which data is inputted from clientScript
#   DATAFORMAT must be consistent across both programs
# note: could make dataformat into a dict for alternative naming
# ie: sensor2:val1
# should change to an dictionary that matches to index ie: 1: "id"
DATAFORMAT = ["id", "time", "h2", "isobutylene", "propane", "ammonia",
              "chlorine", "vis", "co", "temperature", "humidity",
              "no", "no2", "nox"]

DATAINDICES = {
    0: "id",
    1: "time",
    2: "h2",
    3: "isobutylene",
    4: "propane",
    5: "ammonia",
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
    "propane": "LEL%",
    "ammonia": "ppm",
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
    "propane": "C3H8",
    "ammonia": "NH3",
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
    "propane": [0, 100],
    "ammonia": [0, 100],
    "chlorine": [0, 20],
    "vis": [0, 100],
    "co": [0, 300],
    "temperature": [-40, 100],
    "humidity": [0, 100],
    "no": [0, 100],
    "no2": [0, 10],
    "nox": [0, 100],
}

''' end of section '''

# this constant does nothing. It should only help as a notepad to
#   track modbus slave setup
SLAVEIDS = {
    1: "h2",
    2: "isobutylene",
    3: "propane",
    4: "ammonia",
    5: "chlorine",
    6: "viconox",
}

# scales val on a 800-4000 scale to a different, specified scale


def scale800_4000(val, scale):
    ratio = (val - 800) / 3200
    additional = (scale[1] - scale[0]) * ratio
    return scale[0] + additional


def readSensepoint(instrument, gas):
    try:
        retval = instrument.read_register(31000, 0, 4)
        trueVal = scale800_4000(retval, DATABOUNDS[gas])
        return trueVal
    except Exception as e:
        return "None"


def readViconoxValue(instrument, address, rnd):
    try:
        if rnd == 0:
            retval = int(instrument.read_float(address, 4, 2, 0))
        else:
            retval = round(instrument.read_float(address, 4, 2, 0), rnd)
        return retval
    except Exception as e:
        return "None"


def readViconox(instrument):
    # note: decimal places are determined by the precision of the instrument

    # visibility, 1 decimal place
    vis = readViconoxValue(instrument, 10500, 1)

    # co, 1 dec. place
    co = readViconoxValue(instrument, 10502, 1)

    # temperature, 1 dec. place
    temperature = readViconoxValue(instrument, 10504, 1)

    # humidity, 0 dec. place
    humidity = readViconoxValue(instrument, 10506, 0)

    # no, 1 dec. place
    no = readViconoxValue(instrument, 10508, 1)

    # no2, 2 dec. place
    no2 = readViconoxValue(instrument, 10510, 2)

    # nox, 1 dec place
    nox = readViconoxValue(instrument, 10512, 1)

    retArr = [vis, co, temperature, humidity, no, no2, nox]

    return retArr


def collectSensorData(id):
    # sensepoint sensor 1
    # note: verify path exists and is correct
    instrument1 = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    instrument1.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode

    # sensor configurations
    # since all instruments use the same input usb, configuring one sensor
    #    is the same as configuring the rest
    instrument1.serial.baudrate = 9600        # Baud
    instrument1.serial.bytesize = 8
    instrument1.serial.parity = serial.PARITY_EVEN
    instrument1.serial.stopbits = 1
    instrument1.serial.timeout = 0.05          # seconds

    # sensepoint sensor 2
    instrument2 = minimalmodbus.Instrument('/dev/ttyUSB0', 2)
    instrument2.mode = minimalmodbus.MODE_RTU

    # sensepoint sensor 3
    instrument3 = minimalmodbus.Instrument('/dev/ttyUSB0', 3)
    instrument3.mode = minimalmodbus.MODE_RTU

    # sensepoint sensor4
    instrument4 = minimalmodbus.Instrument('/dev/ttyUSB0', 4)
    instrument4.mode = minimalmodbus.MODE_RTU

    # sensepoint sensor5
    instrument5 = minimalmodbus.Instrument('/dev/ttyUSB0', 5)
    instrument5.mode = minimalmodbus.MODE_RTU

    # Viconox sensor 1 (id 6)
    instrument6 = minimalmodbus.Instrument('/dev/ttyUSB0', 6)
    instrument6.mode = minimalmodbus.MODE_RTU

    # querying multiple sensors successively is not possible without these lines
    instrument1.close_port_after_each_call = True
    instrument2.close_port_after_each_call = True
    instrument3.close_port_after_each_call = True
    instrument4.close_port_after_each_call = True
    instrument5.close_port_after_each_call = True
    instrument6.close_port_after_each_call = True

    while True:
        curTime = str(int(time.time()))
        retArr = [str(id), curTime]

        h2 = readSensepoint(instrument1, "h2")
        isobutylene = readSensepoint(instrument2, "isobutylene")
        propane = readSensepoint(instrument3, "propane")
        ammonia = readSensepoint(instrument4, "ammonia")
        chlorine = readSensepoint(instrument5, "chlorine")

        values = readViconox(instrument6)
        vis = values[0]
        co = values[1]
        temp = values[2]
        humidity = values[3]
        no = values[4]
        no2 = values[5]
        nox = values[6]

        retArr = [str(id), curTime, h2, isobutylene, propane,
                  ammonia, chlorine, vis, co, temp, humidity, no, no2, nox]

        return retArr
