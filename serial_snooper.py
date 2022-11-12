import logging

import serial
from pymodbus.factory import ClientDecoder, ServerDecoder
from pymodbus.transaction import ModbusRtuFramer

#import pymodbus
#from pymodbus.transaction import ModbusRtuFramer
#from pymodbus.utilities import hexlify_packets
#from binascii import b2a_hex
# from time import sleep


logger = logging.getLogger()
class SerialSnooper:
    kMaxReadSize = 128
    kByteLength = 10
    processedFramesCounter = 0
    interceptedResponseFramesCounter = 0

    def __init__(self, port, baud=9600):
        logger.debug('SerialSnooper.__init__')
        self.port = port
        self.baud = baud
        self.connection = serial.Serial(port, baud, timeout=float(
            self.kByteLength*self.kMaxReadSize)/baud)
        self.client_framer = ModbusRtuFramer(decoder=ClientDecoder())
        self.server_framer = ModbusRtuFramer(decoder=ServerDecoder())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self.connection.open()

    def close(self):
        self.connection.close()

    def server_packet_callback(self, *args, **kwargs):
        arg = 0
        for msg in args:
            func_name = str(type(msg)).split(
                '.')[-1].strip("'><").replace("Request", "")
            logger.info(logger, "Master-> ID: {}, Function: {}: {}".format(
                msg.unit_id, func_name, msg.function_code))
            try:
                logger.info("Address: {}".format(msg.address))
            except AttributeError:
                pass
            try:
                logger.info("Count: {}".format(msg.count))
            except AttributeError:
                pass
            try:
                logger.info("Data: {}".format(msg.values))
            except AttributeError:
                pass
            arg += 1
            logger.info('{}/{}\n'.format(arg, len(args)))

    def client_packet_callback(self, *args, **kwargs):
        self.interceptedResponseFramesCounter += 1
        arg = 0
        for msg in args:
            func_name = str(type(msg)).split(
                '.')[-1].strip("'><").replace("Request", "")
            logger.info("Slave-> ID: {}, Function: {}: {}".format(
                msg.unit_id, func_name, msg.function_code))
            try:
                logger.info("Address: {}".format(msg.address))
            except AttributeError:
                pass
            try:
                logger.info("Count: {}".format(msg.count))
            except AttributeError:
                pass
            try:
                logger.info("Data: {}".format(msg.values))
            except AttributeError:
                pass
            arg += 1
            logger.info('{}/{}\n'.format(arg, len(args)))

    def read_raw(self, n=16):
        return self.connection.read(n)

    def process(self, data):
        if len(data) <= 0:
            return
        self.processedFramesCounter += 1
        try:
            logger.debug("Check Client")
            self.client_framer.processIncomingPacket(
                data, self.client_packet_callback, unit=None, single=True)
        except (IndexError, TypeError, KeyError) as e:
            logger.debug(e)
            pass
        try:
            logger.debug("Check Server")
            self.server_framer.processIncomingPacket(
                data, self.server_packet_callback, unit=None, single=True)
            pass
        except (IndexError, TypeError, KeyError) as e:
            logger.debug(e)
            pass

    def get_statistics(self):
        if (self.processedFramesCounter==0):
            return 0
        return (1 - (self.processedFramesCounter - self.interceptedResponseFramesCounter) / self.processedFramesCounter) * 100

