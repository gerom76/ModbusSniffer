import logging
import threading
import time
from app.web_app import get_app, setup_webapp_api, update_smartmeter

from common.smartLogger import setup_logger

setup_logger(__package__)

import sys

from serial_snooper import SerialSnooper

logger = logging.getLogger()

def run_webserver(app: any):
    logger.info("Web server thread starting")
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    logger.info("Web server thread finishing")

def run_sniffer(serialSnooper: SerialSnooper, port, baud, slave_address):
    read_size = 128
    logger.info(f"Starting sniffing for port:{port} baud:{baud} read_size:{read_size} slave_address:{slave_address}")
    while True:
        data = serialSnooper.read_raw(read_size)
        if len(data):
            #logger.debug(data)
            serialSnooper.process(data, slave_address)
            statistics = serialSnooper.get_statistics()
            logger.debug(f"Statistics: {statistics}")
            update_smartmeter(statistics)
        # sleep(float(1)/ss.baud)
    logger.info("Sniffer thread  finishing")

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

    slave_address = 1

    setup_webapp_api()
    #sys.exit(0)
    ss = SerialSnooper(port, baud)

    web_server_thread = threading.Thread(target=run_webserver, args=(get_app(),), daemon=True)
    sniffer_thread = threading.Thread(target=run_sniffer, args=(ss, port, baud, slave_address), daemon=True)

    logger.info("Starting threads")
    web_server_thread.start()
    time.sleep(1)
    sniffer_thread.start()

    web_server_thread.join()
    sniffer_thread.join()

    logger.info("Finished threads")
    sys.exit(0)
