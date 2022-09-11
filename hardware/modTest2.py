import minimalmodbus
import serial
import time

# port name, slave address (in decimal)
instrument1 = minimalmodbus.Instrument('/dev/ttyUSB0', 1)

instrument1.serial.baudrate = 9600        # Baud
instrument1.serial.bytesize = 8
instrument1.serial.parity = serial.PARITY_EVEN
instrument1.serial.stopbits = 1
instrument1.serial.timeout = 0.05          # seconds
instrument1.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode

instrument2 = minimalmodbus.Instrument('/dev/ttyUSB0', 2)
instrument2.mode = minimalmodbus.MODE_RTU

instrument3 = minimalmodbus.Instrument('/dev/ttyUSB0', 3)
instrument3.mode = minimalmodbus.MODE_RTU

instrument4 = minimalmodbus.Instrument('/dev/ttyUSB0', 6)
instrument4.mode = minimalmodbus.MODE_RTU

instrument1.close_port_after_each_call = True
instrument2.close_port_after_each_call = True
instrument3.close_port_after_each_call = True
instrument4.close_port_after_each_call = True


## Read temperature (PV = ProcessValue) ##
# read_register(registeraddress: int, number_of_decimals: int = 0, functioncode: int = 3, signed: bool = False)
# Registernumber, number of decimals
while True:
    try:
        retval = instrument1.read_register(31000, 0, 4)
        print(retval)
        # retval = instrument2.read_registers(31010, 2, 4)
        # print(retval)
        # retval = instrument2.read_float(31010, 4, 2, 0)
        # print(retval)
        # retval = instrument2.read_registers(31209, 2, 4)
        # print(retval)
        # retval = instrument1.read_float(31209, 4, 2, 0)
        # print(retval)
        # retval = instrument1.read_registers(31219, 2, 4)
        # print(retval)
        # retval = instrument1.read_float(31219, 4, 2, 1)
        # print(retval)
        # retval = instrument1.read_registers(31223, 2, 4)
        # print(retval)
        # retval = instrument1.read_float(31223, 4, 2, 2)
        # print(retval)
        # retval = instrument4.read_register(10504, 0, 4)
        # print(retval)
        # retval = instrument4.read_registers(10504, 2, 4)
        # print(retval)
        retval = instrument4.read_float(10500, 4, 2, 0)
        print(retval)
        retval = instrument4.read_float(10502, 4, 2, 0)
        print(retval)
        retval = instrument4.read_float(10504, 4, 2, 0)
        print(retval)
        retval = instrument4.read_float(10506, 4, 2, 0)
        print(retval)
        retval = instrument4.read_float(10508, 4, 2, 0)
        print(retval)
        retval = instrument4.read_float(10510, 4, 2, 0)
        print(retval)
        retval = instrument4.read_float(10512, 4, 2, 0)
        print(retval)

        # retval = instrument2.read_register(31000, 0, 4)
        # print(retval)
        # retval = instrument3.read_register(31000, 0, 4)
        # print(retval)
        # retval = instrument4.read_register(10504, 0, 4)
        # print(retval)
        # # retval = instrument3.read_register(31000, 0, 4)
        # # print(retval)
    except Exception as e:
        print(e)
    time.sleep(3)
