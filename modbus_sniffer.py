import sys
import logging
import threading
import time

from common.smartLogger import setup_logger
setup_logger(__package__)

from api.web_app import get_app, setup_webapp_api
from engine.serial_snooper import SerialSnooper

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def run_webserver(app: any):
    logger.warning("Web server thread starting")
    from waitress import serve
    serve(app, host="0.0.0.0", port=8081)
    logger.warning("Web server thread finishing")

def run_sniffer(serialSnooper: SerialSnooper, port, baud, slave_address, method):
    logger.warning(f"Starting sniffing for port:{port} baud:{baud} slave_address:{slave_address}")
    if method == 'generic':
        serialSnooper.run_method_generic(slave_address)
    elif method == 'optimized':
        serialSnooper.run_method_optimized(slave_address)
    else:
        logger.warning("Sniffer thread finishing - invalid method")

if __name__ == "__main__":
    logger.debug("__main__.Begin")
    baud = 9600
    slave_address = 1
    method ='generic'
    in_memory = True
    try:
        port = sys.argv[1]
    except IndexError:
        print(f"Usage: python3 {sys.argv[0]} device [baudrate, default={baud}] [slave_address, default={slave_address}] [method, default={method}]")
        sys.exit(-1)
    try:
        baud = int(sys.argv[2])
        slave_address = int(sys.argv[3])
        method = sys.argv[4]
    except (IndexError, ValueError):
        pass
    setup_webapp_api(in_memory)
    #sys.exit(0)
    ss = SerialSnooper(port, baud, slave_address)

    web_server_thread = threading.Thread(target=run_webserver, args=(get_app(),), daemon=True)
    sniffer_thread = threading.Thread(target=run_sniffer, args=(ss, port, baud, slave_address, method), daemon=True)

    logger.info("Starting threads")
    web_server_thread.start()
    time.sleep(1)
    sniffer_thread.start()

    web_server_thread.join()
    sniffer_thread.join()

    logger.info("Finished threads")
    sys.exit(0)
