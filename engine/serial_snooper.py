from collections import Counter, OrderedDict
import logging
import serial
from pymodbus.factory import ClientDecoder, ServerDecoder
from api.web_app import update_sniffing_quality
from engine.chint666_adapter import Chint666LegacyAdapter, Chint666TunedAdapter
from pymodbus.framer.rtu_framer import ModbusRtuFramer
from pymodbus.utilities import (
    checkCRC,
)
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
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
        self.chint666LegacyAdapter = Chint666LegacyAdapter()
        self.client_framer = ModbusRtuFramer(decoder=ClientDecoder())
        self.server_framer = ModbusRtuFramer(decoder=ServerDecoder())
        
        self.frameBuffer =  bytearray()
        self.isProcessingFrame1 = True
        self.frame1Request =  bytearray()
        self.frame2Request =  bytearray()
        self.frame1Response =  bytearray()
        self.frame2Response =  bytearray()

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

    def print_registers(registers: list):
        return ' '.join([str(i)+":"+hex(value) for i, value in enumerate(registers)])

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

    # Optimized flow for string of interlaced request and responses:
    def run_method_optimized(self, slave_address):
        logger.warning(f"Starting Optimized Method")
        total_data: OrderedDict = OrderedDict()
        start_address = ''
        while True:
            message = self.read_in_waiting()
            if len(message) <= 0: continue
            
            logger.debug(f"message[{len(message)}]: {message.hex()}")
            
            if len(message)==8:
                logger.debug(f"request (current): {message.hex()}")
                if self.isProcessingFrame1:
                    self.frame1Request = message
                    self.frame2Response = self.frameBuffer
                    self.isProcessingFrame1 = False
                else:
                    self.frame2Request = message
                    self.frame1Response = self.frameBuffer
                    self.isProcessingFrame1 = True
                self.frameBuffer = bytearray()
                                    
                # logger.info(f"F1 {self.frame1Request.hex()} {self.frame1Response.hex()}")
                # logger.info(f"F2 {self.frame2Request.hex()} {self.frame2Response.hex()}")
                
                if self.isProcessingFrame1 and len(self.frame1Request)>0 and len(self.frame1Response)>0:
                    start_address, data = self.process_optimized(self.frame1Request, self.frame1Response, slave_address)
                if not self.isProcessingFrame1 and len(self.frame2Request)>0 and len(self.frame2Response)>0:
                    start_address, data = self.process_optimized(self.frame2Request, self.frame2Response, slave_address)

                if start_address=='2000':
                    total_data = data
                elif start_address=='101e':
                    total_data.update(data)
                
                if len(start_address)>0 and len(total_data)>22:
                    logger.info(f'Ready to pass data: {total_data}')
                    total_data = OrderedDict()

            else:
                self.frameBuffer += message

    def process_optimized(self, request, response, slave_address):
        logger.info(f'Processing request={request.hex()} response={response.hex()}')
        try:
            is_valid = SerialSnooper.check_message(request)
            if is_valid:
                slave_adr, func_code, start_address, quantity = SerialSnooper.decode_request_message(request)
                
                if slave_adr != slave_address: return
                
                is_valid = SerialSnooper.check_message(response)
                if is_valid:
                    slave_adr, func_code, byte_count = SerialSnooper.decode_response_message(response)
                    logger.debug(f'Decoding response: func_code={func_code} start_address=0x{start_address} quantity=0x{quantity} byte_count={byte_count}')
                    payload = SerialSnooper.extract_payload(response, byte_count)
                    decoder = SerialSnooper.load_decoder(payload)
                    SerialSnooper.log_registry(response, byte_count, decoder)
                    chint666Adaper = Chint666TunedAdapter(decoder)
                    if start_address=='2000':
                        data = chint666Adaper.decode_electricity()
                    elif start_address=='101e':
                        data = chint666Adaper.decode_power()
                    if data:
                        return start_address, data
                    else:
                        logger.error(f'Invalid data: {data}')
        except Exception as ex:
            logger.error(f'Processing exception={ex} Request={request} Response={response}')
            pass

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
            self.chint666LegacyAdapter.process_meter_response(msg)

    def get_statistics(self):
        if (self.processedFramesCounter==0):
            return 0
        return ((self.interceptedResponseFramesCounter) / self.processedFramesCounter) * 100

