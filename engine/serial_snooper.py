import logging
import serial
from pymodbus.factory import ClientDecoder, ServerDecoder
from pymodbus.transaction import ModbusRtuFramer
from api.web_app import update_sniffing_quality
from engine.chint666_adapter import Chint666Adapter
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
    
    def __init__(self, port, baud=9600, slave_address=1):
        logger.debug('SerialSnooper.__init__')
        self.port = port
        self.baud = baud
        self.slave_address = slave_address
        self.serial = serial.Serial(port, baud, timeout=float(
            self.kByteLength*self.kMaxReadSize)/baud)
        self.client_framer = ModbusRtuFramer(decoder=ClientDecoder())
        self.server_framer = ModbusRtuFramer(decoder=ServerDecoder())
        self.responseBuffer =  bytearray()
        self.chint666Adapter = Chint666Adapter()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self.serial.open()

    def close(self):
        self.serial.close()

    def read_raw(self, n=16):
        # response = self.serial.read(self.serial.in_waiting)
        response = self.serial.read(n)
        self.responseBuffer += response
        return response

    def server_packet_callback(self, *args, **kwargs):
        logger.debug(f"responseBuffer: {self.responseBuffer.hex()}")
        # TODO: start recording for this buffer till next master packet
        self.responseBuffer = bytearray()
        arg = 0
        address = 'unknown'
        count = 0
        values = 'empty'
        for msg in args:
            func_name = str(type(msg)).split(
                '.')[-1].strip("'><").replace("Request", "")
            try:
                address = msg.address
            except AttributeError:
                pass
            try:
                count = msg.count
            except AttributeError:
                pass
            try:
                values = msg.values
            except AttributeError:
                pass
            arg += 1
            logger.info(f"Master Request-> ID: {msg.unit_id} arg({arg}/{len(args)}) Function: {func_name}: {msg.function_code} address: {address} ({count}) values:{values}")

    def client_packet_callback(self, *args, **kwargs):
        self.interceptedResponseFramesCounter += 1
        arg = 0
        for msg in args:
            func_name = str(type(msg)).split(
                '.')[-1].strip("'><").replace("Response", "")
            arg += 1
            logger.info(f"Slave Response-> ID: {msg.unit_id}, arg({arg}/{len(args)}) Function: {func_name}: {msg.function_code}")
            self.chint666Adapter.process_meter_response(msg)

    def process(self, data, slave_address):
        if len(data) <= 0:
            return
        logger.debug(f'data: {data.hex()}')
        self.processedFramesCounter += 1
        try:
            logger.debug("Check Client")
            self.client_framer.processIncomingPacket(
                data, self.client_packet_callback, unit=slave_address, single=True)
        except (IndexError, TypeError, KeyError) as e:
            logger.debug(e)
            pass
        try:
            logger.debug("Check Server")
            self.server_framer.processIncomingPacket(
                data, self.server_packet_callback, unit=slave_address, single=True)
            pass
        except (IndexError, TypeError, KeyError) as e:
            logger.debug(e)
            pass
        statistics = self.get_statistics()
        update_sniffing_quality(statistics)

    def get_statistics(self):
        if (self.processedFramesCounter==0):
            return 0
        return ((self.interceptedResponseFramesCounter) / self.processedFramesCounter) * 100

