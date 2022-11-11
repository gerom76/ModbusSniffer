import logging
import sys
from common.smartLogger import configure_handler
from serial_snooper import SerialSnooper

logging.basicConfig(level=logging.DEBUG)
file_handler = configure_handler()
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

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
