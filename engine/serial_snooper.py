import logging
import serial
from pymodbus.factory import ClientDecoder, ServerDecoder
# from pymodbus.transaction import ModbusRtuFramer
from api.web_app import update_sniffing_quality
from engine.chint666_adapter import Chint666Adapter
from pymodbus.framer.rtu_framer import ModbusRtuFramer
from pymodbus.utilities import (
    checkCRC,
)
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
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
        self.chint666Adapter = Chint666Adapter()
        self.client_framer = ModbusRtuFramer(decoder=ClientDecoder())
        self.server_framer = ModbusRtuFramer(decoder=ServerDecoder())
        
        self.frameBuffer1 =  bytearray()
        # self.frameBuffer2 =  bytearray()
        self.isProcessingFrame1 = True
        self.frame1Request =  bytearray()
        self.frame2Request =  bytearray()
        self.frame1Response =  bytearray()
        self.frame2Response =  bytearray()
        # self.request1Adresss = ''
        # self.request2Adresss = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self.serial.open()

    def close(self):
        self.serial.close()

    def read_raw(self, n=16):
        return self.serial.read(n)

    def read_in_waiting(self):
        return self.serial.read(self.serial.in_waiting)

###################################################
# https://github.com/eterey/pymodbus3/blob/master/examples/contrib/message-parser.py

    def check_message(message: bytearray):
        size = len(message)
        crc = message[size - 2 : size]
        crc_val = (int(crc[0]) << 8) + int(crc[1])
        return checkCRC(message[0:size-2], crc_val)
    
    def decode_request_message(message: bytearray):
        slave_adr = int(message[0])
        func_code = int(message[1])
        start_address = (message[2:4]).hex()
        quantity = (message[4:6]).hex()
        return slave_adr, func_code, start_address, quantity

    def decode_response_message(message: bytearray):
        slave_adr = int(message[0])
        func_code = int(message[1])
        byte_count = (message[2])
        return slave_adr, func_code, byte_count

    def extract_payload(data: bytearray, byte_count: int):
        payload = []
        for i in range(byte_count):
            payload.append(bytes(data[i+3:i+4]))
        return payload
    
    def load_decoder(payload: list):
        builder = BinaryPayloadBuilder(payload, repack=False, byteorder=Endian.Big, wordorder=Endian.Big)
        registers = builder.to_registers()
        logger.debug(f'load_decoder-registers: {registers}')
        # print(registers)
        return SerialSnooper.prepare_decoder(registers)

    def prepare_decoder(registers: list):
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big, wordorder=Endian.Big)
        return decoder

    def log_registry(message: bytearray, byte_count: int, decoder: BinaryPayloadDecoder):
        logger.debug(f'Registry for message hex: {message.hex()} byte_count: {byte_count}')
        decoder.reset()
        for i in range(int(byte_count/4)):
            entry = message[(i*4+3):(i*4+7)]
            logger.debug(f'{i}: {bytes(entry)} hex: {entry.hex()} value: {decoder.decode_32bit_float()}')
        decoder.reset()

    def run_method_optimized(self, slave_address):
        logger.warning(f"Starting method Optimized")
        while True:
            message = self.read_in_waiting()
            if len(message) > 0:
                logger.debug(f"message[{len(message)}]: {message.hex()}")
                
                if len(message)==8:
                    logger.info(f"request (current): {message.hex()}")
                    # self.client_framer.addToFrame(message)
                    # data = self.client_framer.getRawFrame() # if error else self.getFrame()
                    # logger.info(f"request (current): data {data}")
                    # result = self.client_framer.decoder.decode(data)
                    # logger.info(f"request (current): result {result}")
                    # self.client_framer.resetFrame()
                    
                    self.server_framer.addToFrame(message)
                    data = self.server_framer.getRawFrame() # if error else self.getFrame()
                    logger.info(f"request (current): data {data}")
                    result = self.server_framer.decoder.decode(data)
                    logger.info(f"request (current): result {result}")
                    self.server_framer.resetFrame()
                    
                    
                    # if self.client_framer.checkFrame():
                    #     data = self.client_framer.getRawFrame() # if error else self.getFrame()
                    #     logger.info(f"request (current): data {data}")
                    #     result = self.client_framer.decoder.decode(data)
                    #     logger.info(f"request (current): result {result}")
                    #     self.client_framer.populateResult(result)
                    #     self.client_framer.advanceFrame()
                    # else:
                    #     logger.warning(f"invalid client message: {message.hex()}")
                    #     self.client_framer.resetFrame()
                        
                    # self.server_framer.addToFrame(message)
                    # if self.server_framer.checkFrame():
                    #     data = self.server_framer.getRawFrame() # if error else self.getFrame()
                    #     logger.info(f"request (current): data {data}")
                    #     result = self.server_framer.decoder.decode(data)
                    #     logger.info(f"request (current): result {result}")
                    #     self.server_framer.populateResult(result)
                    #     self.server_framer.advanceFrame()
                    # else:
                    #     logger.warning(f"invalid server message: {message.hex()}")
                    #     self.server_framer.resetFrame()
                        
                        
                        
                    # if self.client_framer.checkFrame():
                        # self.client_framer.advanceFrame()
                    #self.client_framer.processIncomingPacket(message, self.master_packet_callback2, unit=slave_address, single=True)
                    
                    logger.info(f"response (previous): {self.frameBuffer1.hex()}")
                    # self.server_framer.addToFrame(self.frameBuffer1)
                    # if self.server_framer.checkFrame():
                        # self.server_framer.advanceFrame()
                    #self.server_framer.processIncomingPacket(self.frameBuffer1, self.slave_packet_callback2, unit=slave_address, single=True)
                    
                    if self.isProcessingFrame1:
                        self.frame1Request = message
                        self.frame2Response = self.frameBuffer1
                        self.isProcessingFrame1 = False
                    else:
                        self.frame2Request = message
                        self.frame1Response = self.frameBuffer1
                        self.isProcessingFrame1 = True
                        
                    logger.info(f"F1 {self.frame1Request.hex()} {self.frame1Response.hex()}")
                    logger.info(f"F2 {self.frame2Request.hex()} {self.frame2Response.hex()}")
                    
                    self.frameBuffer1 = bytearray()
                else:
                    self.frameBuffer1 += message
                    
                # self.process_optimized(message, slave_address)
            # self.frameBuffer1 = self.read_in_waiting()
            # logger.debug(f"frameBuffer1: {self.frameBuffer1.hex()}")
            # self.process_generic(self.frameBuffer1, slave_address)
            # self.frameBuffer2 = self.read_in_waiting()
            # logger.debug(f"frameBuffer2: {self.frameBuffer2.hex()}")
            # self.process_generic(self.frameBuffer2, slave_address)

    def process_optimized(self, message, slave_address):
        logger.debug(f'optimized process: message={message.hex()}')

        self.processedFramesCounter += 1

        try:
            self.client_framer.addToFrame(message)
            if self.client_framer.checkFrame():
                self.client_framer.advanceFrame()
                self.client_framer.processIncomingPacket(message, self.master_packet_callback2, unit=slave_address)
            else: self.check_errors(self.server_framer, message)
        except Exception as ex: 
            self.check_errors(self.server_framer, message)
    
        try:
            self.server_framer.addToFrame(message)
            if self.server_framer.checkFrame():
                self.server_framer.advanceFrame()
                self.server_framer.processIncomingPacket(message, self.slave_packet_callback2, unit=slave_address)
            else: self.check_errors(self.server_framer, message)
        except Exception as ex: 
            self.check_errors(self.server_framer, message)

    def check_errors(self, decoder, message):
        ''' Attempt to find message errors
        :param message: The message to find errors in
        '''
        logger.debug(f'Check_errors: message={message.hex()}')
        pass

    def master_packet_callback2(self, *args, **kwargs):
        # logger.debug(f"responseBuffer: {self.responseBuffer.hex()}")
        # # TODO: start recording for this buffer till next master packet
        # self.responseBuffer = bytearray()
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


    def slave_packet_callback2(self, *args, **kwargs):
        self.interceptedResponseFramesCounter += 1
        arg = 0
        for msg in args:
            func_name = str(type(msg)).split(
                '.')[-1].strip("'><").replace("Response", "")
            arg += 1
            logger.info(f"Slave Response-> ID: {msg.unit_id}, arg({arg}/{len(args)}) Function: {func_name}: {msg.function_code}")
            self.chint666Adapter.process_meter_response(msg)


    # def report(self, message):
    #     ''' The callback to print the message information
    #     :param message: The message to print
    #     '''
    #     print "%-15s = %s" % ('name', message.__class__.__name__)
        # for k,v in message.__dict__.iteritems():
        #     if isinstance(v, dict):
        #         print "%-15s =" % k
        #         for kk,vv in v.items():
        #             print "  %-12s => %s" % (kk, vv)

        #     elif isinstance(v, collections.Iterable):
        #         print "%-15s =" % k
        #         value = str([int(x) for x  in v])
        #         for line in textwrap.wrap(value, 60):
        #             print "%-15s . %s" % ("", line)
        #     else: print "%-15s = %s" % (k, hex(v))
        # print "%-15s = %s" % ('documentation', message.__doc__)
        
        
        
        
        # try:
        #     logger.debug("Using server_framer")
        #     self.server_framer.processIncomingPacket(
        #         data, self.master_packet_callback, unit=slave_address, single=True)
        #     pass
        # except (IndexError, TypeError, KeyError) as e:
        #     logger.error(e)
        #     pass
        
        # try:
        #     logger.debug("Using client_framer")
        #     self.client_framer.processIncomingPacket(
        #         data, self.slave_packet_callback, unit=slave_address, single=True)
        # except (IndexError, TypeError, KeyError) as e:
        #     logger.error(e)
        #     pass
        
        # update_sniffing_quality(self.get_statistics())
            
            # time.sleep(float(1)/ss.baud)
            
    # def process_frame(self, requestBuffer, slave_address):
    #     logger.debug(f'process request: requestBuffer={requestBuffer.hex()}')
    #     if len(requestBuffer) <= 0:
    #         return
    #     try:
    #         self.server_framer.processIncomingPacket(
    #             requestBuffer, self.request_packet_callback, unit=slave_address, single=True)
    #         pass
    #     except (IndexError, TypeError, KeyError) as e:
    #         logger.error(e)
    #         pass


    # def request_packet_callback(self, *args, **kwargs):
    #     logger.debug(f"responseBuffer: {self.responseBuffer.hex()}")
    #     # TODO: start recording for this buffer till next master packet
    #     self.responseBuffer = bytearray()
    #     arg = 0
    #     address = 'unknown'
    #     count = 0
    #     for msg in args:
    #         func_name = str(type(msg)).split(
    #             '.')[-1].strip("'><").replace("Request", "")
    #         try:
    #             address = msg.address
    #         except AttributeError:
    #             pass
    #         try:
    #             count = msg.count
    #         except AttributeError:
    #             pass
    #         arg += 1
    #     logger.info(f"Master Request-> ID: {msg.unit_id} arg({arg}/{len(args)}) Function: {func_name}: {msg.function_code} address: {address} ({count}) ")
    #     if self.isProcessingRequest1:
    #         self.request1Adresss = address
    #         self.isProcessingRequest1 = False
    #     else:
    #         self.request2Adresss = address
    #         self.isProcessingRequest1 = True

######################################################

    def run_method_generic(self, slave_address):
        read_size = 128
        logger.warning(f"Starting method Generic: read_size:{read_size}")
        while True:
            data = self.read_raw(read_size)
            self.process_generic(data, slave_address)
            # time.sleep(float(1)/ss.baud)

    def process_generic(self, data, slave_address):
        logger.debug(f'generic process: data={data.hex()}')
        if len(data) <= 0:
            return

        self.processedFramesCounter += 1
        try:
            logger.debug("Check Client")
            self.client_framer.processIncomingPacket(
                data, self.slave_packet_callback, unit=slave_address, single=True)
        except (IndexError, TypeError, KeyError) as e:
            logger.error(e)
            pass
        try:
            logger.debug("Check Server")
            self.server_framer.processIncomingPacket(
                data, self.master_packet_callback, unit=slave_address, single=True)
            pass
        except (IndexError, TypeError, KeyError) as e:
            logger.error(e)
            pass

        update_sniffing_quality(self.get_statistics())

    def master_packet_callback(self, *args, **kwargs):
        # logger.debug(f"responseBuffer: {self.responseBuffer.hex()}")
        # # TODO: start recording for this buffer till next master packet
        # self.responseBuffer = bytearray()
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

    def slave_packet_callback(self, *args, **kwargs):
        self.interceptedResponseFramesCounter += 1
        arg = 0
        for msg in args:
            func_name = str(type(msg)).split(
                '.')[-1].strip("'><").replace("Response", "")
            arg += 1
            logger.info(f"Slave Response-> ID: {msg.unit_id}, arg({arg}/{len(args)}) Function: {func_name}: {msg.function_code}")
            self.chint666Adapter.process_meter_response(msg)

    def get_statistics(self):
        if (self.processedFramesCounter==0):
            return 0
        return ((self.interceptedResponseFramesCounter) / self.processedFramesCounter) * 100

