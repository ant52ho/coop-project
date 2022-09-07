import minimalmodbus
import serial
import time

# some sensor constants
# format: [name] [unit] [span]

# h2 LEL% 0-100
# isobutylene ppm 0-100
# propane LEL% 0-100
# ammonia ppm 0-100
# chlorine ppm 0-20


def readH2(instrument):

    return


def readIsobutylene(instrument):
    return


def readPropane(instrument):
    return


def readAmmonia(instrument):
    return


def readChlorine(instrument):
    return


def readViconox(instrument):
    return


def collectSensorData():
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

        h2 = readH2(instrument1)
        isobutylene = readIsobutylene(instrument2)
        propane = readPropane(instrument3)
        ammonia = readAmmonia(instrument4)
        chlorine = readChlorine(instrument5)

        values = readViconox(instrument6)
        vis = values[0]
        co = values[1]
        temp = values[2]
        humidity = values[3]
        no = values[4]
        no2 = values[5]
        nox = values[6]

        # data format: f:data:id,val,val,val...
        select = 'f:data:' + ','.join(retArr)

        print(select)

        retval = send(select, edgeClient)

        # if server doesn't respond
        if not retval:
            break

        # delay before next query
        time.sleep(3)
