import logging

from common.smartLogger import setup_logger

setup_logger(__package__)

import sys

from serial_snooper import SerialSnooper

logger = logging.getLogger()

if __name__ == "__main__":
    logger.debug("__main__.Begin")
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
    logger.info(f"Started sniffing for port:{port} baud:{baud}")
    with SerialSnooper(port, baud) as ss:
        while True:
            data = ss.read_raw(16)
            # if len(data):
            #     logger.debug(data)
            response = ss.process(data)
            # sleep(float(1)/ss.baud)
    sys.exit(0)
