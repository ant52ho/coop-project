from pymodbus.client import ModbusSerialClient

PORT = 'COM3'  # this may not work

if __name__ == '__main__':

    # array for slaves
    slavesArr = [1]

    client = ModbusSerialClient(
        port=PORT,  # serial port
        # Common optional paramers:
        #    framer=ModbusRtuFramer,
        #    timeout=10,
        #    retries=3,
        #    retry_on_empty=False,
        #    close_comm_on_error=False,.
        #    strict=True,
        # Serial setup parameters
        #    baudrate=9600,
        #    bytesize=8,
        #    parity="N",
        #    stopbits=1,
        #    handle_local_echo=False,
    )

    print("### Client starting")
    client.connect()

    # address, count, slave
    for slaveId in slavesArr:

        val = client.read_holding_registers(
            address=31000, count=1, slave=slaveId)
        print(val)

    client.close()
