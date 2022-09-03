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
instrument1.close_port_after_each_call = True
retval = instrument1.read_register(31000, 0, 4)
print(retval)
