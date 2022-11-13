import logging

from common.smartLogger import setup_logger

setup_logger(__package__)

import sys

from flask import Flask

from serial_snooper import SerialSnooper

logger = logging.getLogger()
app = Flask(__name__)
@app.route('/')
def example():
    return '{"name":"Bob"}'

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
    logger.debug(f"Starting server")
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

    logger.info(f"Starting sniffing for port:{port} baud:{baud}")
    with SerialSnooper(port, baud) as ss:
        while True:
            data = ss.read_raw(16)
            if len(data):
            #     logger.debug(data)
                ss.process(data)
                logger.info(f"Statistics: {ss.get_statistics()}")
            # sleep(float(1)/ss.baud)
    sys.exit(0)
