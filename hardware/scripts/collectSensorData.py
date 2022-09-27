import minimalmodbus
import serial
import time
from projectConf import *
# scales val on a 800-4000 scale to a different, specified scale


def scale800_4000(val, scale):
    ratio = (val - 800) / 3200
    additional = (scale[1] - scale[0]) * ratio
    return scale[0] + additional


def readSensepoint(instrument, gas):
    try:
        retval = instrument.read_register(31000, 0, 4)
        trueVal = scale800_4000(retval, DATABOUNDS[gas])
        return str(trueVal)
    except Exception as e:
        return "None"


def readViconoxValue(instrument, address, rnd):
    try:
        if rnd == 0:
            retval = int(instrument.read_float(address, 4, 2, 0))
        else:
            retval = round(instrument.read_float(address, 4, 2, 0), rnd)
        return str(retval)
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
        ammonia = readSensepoint(instrument3, "ammonia")
        propane = readSensepoint(instrument4, "propane")
        chlorine = readSensepoint(instrument5, "chlorine")

        values = readViconox(instrument6)
        vis = values[0]
        co = values[1]
        temp = values[2]
        humidity = values[3]
        no = values[4]
        no2 = values[5]
        nox = values[6]

        retArr = [str(id), curTime, h2, isobutylene, ammonia,
                  propane, chlorine, vis, co, temp, humidity, no, no2, nox]

        return retArr


if __name__ == "__main__":
    while True:
        data = collectSensorData(2)
        print(data)
        time.sleep(3)
