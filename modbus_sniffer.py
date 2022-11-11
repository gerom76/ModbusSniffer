import logging
import sys
#import pymodbus
#from pymodbus.transaction import ModbusRtuFramer
#from pymodbus.utilities import hexlify_packets
#from binascii import b2a_hex
from time import sleep

import serial
from pymodbus.factory import ClientDecoder, ServerDecoder
from pymodbus.transaction import ModbusRtuFramer

from common.smartLogger import configure_handler
from serial_snooper import SerialSnooper

logging.basicConfig(filename='modbus_sniffer.log',filemode='w', level=logging.DEBUG)
file_handler = configure_handler()
logger = logging.getLogger()
logger.addHandler(file_handler)
#logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    baud = 9600
    try:
        port = sys.argv[1]
    except IndexError:
        print("Usage: python3 {} device [baudrate, default={}]".format(
            sys.argv[0], baud))
        sys.exit(-1)
    try:
        baud = int(sys.argv[2])
    except (IndexError, ValueError):
        pass
    with SerialSnooper(port, baud) as ss:
        while True:
            data = ss.read_raw(16)
            if len(data):
                ss.log_wrapper(data)
            response = ss.process(data)
            # sleep(float(1)/ss.baud)
    sys.exit(0)
