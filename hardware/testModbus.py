from pymodbus.client.sync import (
    ModbusSerialClient,
    ModbusTcpClient,
    ModbusTlsClient,
    ModbusUdpClient,
)

# PORT = 'COM3'  # windows
# PORT = '/dev/ttyUSB0'
PORT = '/dev/ttyUSB0'

if __name__ == '__main__':

    # array for slaves
    slavesArr = [1]

    # note: needs to have same setup as rest of nodes
    client = ModbusSerialClient(
        port=PORT,  # serial port
        # timeout=10,
        # retries=3,
        # retry_on_empty=True,
        # close_comm_on_error=True,
        baudrate=9600,
        # bytesize=8,
        parity="E",  # None, Even, Odd
        # stopbits=1,
        #    handle_local_echo=False,
    )

    print("### Client starting")
    val = client.connect()
    print(client.is_socket_open())
    print(val)
    val = client.read_holding_registers(
        address=31001, count=10, slave=1)
    print(val)

    # # address, count, slave
    # for slaveId in slavesArr:

    #     val = client.read_holding_registers(
    #         address=31000, count=1, slave=slaveId)
    #     print(val)

    client.close()
