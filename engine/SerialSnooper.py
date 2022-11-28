from collections import OrderedDict
from datetime import datetime
import logging
import serial
import time
from pymodbus.factory import ClientDecoder, ServerDecoder
from api.web_app import update_smart_meter, update_smart_meter_legacy, update_statistics
from engine.chint666adapter import Chint666LegacyAdapter, Chint666TunedAdapter
from pymodbus.framer.rtu_framer import ModbusRtuFramer
# from pymodbus.transaction import ModbusRtuFramer
from pymodbus.utilities import (
    checkCRC,
)
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from common.RepeatedTimer import RepeatedTimer
#from pymodbus.utilities import hexlify_packets
#from binascii import b2a_hex
# from time import sleep

logger = logging.getLogger()
class SerialSnooper:
    kMaxReadSize = 128
    kByteLength = 10
    processedFramesCounter = 0
    interceptedResponseFramesCounter = 0
    errorCounter = 0
    lastError = ''
    
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

    def reset_statistics(self):
        self.processedFramesCounter = 0
        self.interceptedResponseFramesCounter = 0
        self.errorCounter = 0
        
    def get_statistics(self):
        sniffingRate = 0
        errorRate = 0
        readingDate = datetime.now().strftime("%Y/%m/%d/ %H:%M:%S.%f")
        if (self.processedFramesCounter>0):
            sniffingRate = ((self.interceptedResponseFramesCounter) / self.processedFramesCounter) * 100
            errorRate = ((self.errorCounter) / self.processedFramesCounter) * 100
        
        errorCounter = self.errorCounter
        processedFramesCounter = self.processedFramesCounter
        lastError = self.lastError
        return readingDate, errorCounter, processedFramesCounter, errorRate, sniffingRate, lastError

    def commit_lazy_statistics(self):
        readingDate, errorCounter, processedFramesCounter, errorRate, sniffingRate, lastError = self.get_statistics()
        # logger.warn(f"commit_lazy_statistics: {readingDate} {processedFramesCounter} {sniffingRate} {errorRate}")
        update_statistics(readingDate, errorCounter, processedFramesCounter, errorRate, sniffingRate, lastError)
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
        self.reset_statistics()
        frameBuffer =  bytearray()
        isProcessingFrame1 = True
        frame1Request =  bytearray()
        frame2Request =  bytearray()
        frame1Response =  bytearray()
        frame2Response =  bytearray()
        total_data: OrderedDict = OrderedDict()
        start_address = ''
        rt = RepeatedTimer(1, self.commit_lazy_statistics)
        rt.start()
        while True:
            try:
                time.sleep(float(1)/self.baud) # to reduce cpu stress
                message = self.read_in_waiting()
                if len(message) <= 0: continue
                self.processedFramesCounter += 1
                logger.debug(f"message[{len(message)}]: {message.hex()}")
                
                if len(message)==8:
                    logger.debug(f"request (current): {message.hex()}")
                    if isProcessingFrame1:
                        frame1Request = message
                        frame2Response = frameBuffer
                        isProcessingFrame1 = False
                    else:
                        frame2Request = message
                        frame1Response = frameBuffer
                        isProcessingFrame1 = True
                    frameBuffer = bytearray()
                                        
                    # logger.info(f"F1 {frame1Request.hex()} {frame1Response.hex()}")
                    # logger.info(f"F2 {frame2Request.hex()} {frame2Response.hex()}")
                    
                    if isProcessingFrame1 and len(frame1Request)>0 and len(frame1Response)>0:
                        start_address, data = self.process_optimized(frame1Request, frame1Response, slave_address)
                    if not isProcessingFrame1 and len(frame2Request)>0 and len(frame2Response)>0:
                        start_address, data = self.process_optimized(frame2Request, frame2Response, slave_address)

                    if start_address=='2000':
                        total_data = data
                    elif start_address=='101e':
                        total_data.update(data)
                    self.interceptedResponseFramesCounter += 1
                    
                    if len(start_address)>0 and len(total_data)>22:
                        logger.debug(f'Ready to pass data: {total_data}')
                        # TODO: slow down updates (measure no of updates per sec)
                        update_smart_meter(total_data)
                        total_data = OrderedDict()

                else:
                    frameBuffer += message
            except Exception as e:
                logger.error(f'run_method_optimized: error:{e}')
                self.errorCounter += 1
                self.lastError = e
                pass # TODO: break program after 10 fails: ERROR [SerialSnooper.run_method_generic:233] run_method_generic: error:device reports readiness to read but returned no data (device disconnected or multiple access on port?) - when usb dongle dettached!
        rt.stop()

    def process_optimized(self, request, response, slave_address):
        logger.info(f'Processing request={request.hex()} response={response.hex()}')
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
                chint666Adaper = Chint666TunedAdapter()
                if start_address=='2000':
                    data = chint666Adaper.decode_electricity(decoder)
                elif start_address=='101e':
                    data = chint666Adaper.decode_power(decoder)
                if data:
                    return start_address, data
                else:
                    logger.error(f'Invalid data: {data}')

######################################################

    def run_method_generic(self, slave_address):
        read_size = 128
        self.reset_statistics()
        logger.warning(f"Starting method Generic: read_size:{read_size}")
        rt = RepeatedTimer(1, self.commit_lazy_statistics)
        rt.start()
        while True:
            try:
                message = self.read_raw(read_size)
                if len(message) <= 0: continue
                self.processedFramesCounter += 1
                self.process_generic(message, slave_address)
                # time.sleep(float(1)/ss.baud)
            except Exception as e:
                logger.error(f'run_method_generic: error:{e}')
                self.errorCounter += 1
                self.lastError = e
                pass # TODO: break program after 10 fails: ERROR [SerialSnooper.run_method_generic:233] run_method_generic: error:device reports readiness to read but returned no data (device disconnected or multiple access on port?) - when usb dongle dettached!
        rt.stop()
    
    def process_generic(self, message, slave_address):
        logger.debug(f'generic process: data={message.hex()}')
        if len(message) <= 0:
            return
        self.client_framer.processIncomingPacket(
            message, self.slave_packet_callback, unit=slave_address, single=True)
        self.server_framer.processIncomingPacket(
            message, self.master_packet_callback, unit=slave_address, single=True)

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
            self.process_meter_response(msg)

    def process_meter_response(self, msg):
        data = ' '.join([str(i)+":"+hex(value) for i, value in enumerate(msg.registers)])
        count = len(msg.registers)
        logger.debug(f'Processing meter: {msg} ([{count}]) \n{data}\n{msg.registers}')
        if count == 60:
            power_data = self.chint666LegacyAdapter.decode_power(msg.registers)
            update_smart_meter_legacy(power_data)
        elif count == 82:
            electricity_data = self.chint666LegacyAdapter.decode_electricity(msg.registers)
            update_smart_meter_legacy(electricity_data)
        else:
            logger.warning(f'Unknown count {count}')