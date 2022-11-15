import logging
from collections import OrderedDict
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from app.web_app import update_electricity, update_power

logger = logging.getLogger()

def process_meter_response(msg):
    try:
        logger.info(f'Processing msg: {msg} {msg.registers}')
        count = len(msg.registers)
        if count == 60:
            logger.debug(f'Power data')
            power_data = decode_power(msg.registers)
            update_power(power_data)
        elif count == 82:
            logger.debug(f'Electricity data')
            electricity_data = decode_electricity(msg.registers)
            # for name, value in iter(electricity_data.items()):
            #     logger.info(f'{name} = {value}')
            update_electricity(electricity_data)
        else:
            logger.debug(f'Unknown address')
    except:
        # logger.error(f'Error processing msg: {msg}')
        pass
    finally:
        logger.debug(f'Finished processing msg: {msg}')


def decode_electricity(registers):
    decoder = BinaryPayloadDecoder.fromRegisters(
        registers, byteorder=Endian.Big, wordorder=Endian.Big)
    dict = OrderedDict(
        [
            ("Uab", decoder.decode_32bit_float()*0.1),
            ("Ubc", decoder.decode_32bit_float()*0.1),
            ("Uca", decoder.decode_32bit_float()*0.1),
            ("Ua", decoder.decode_32bit_float()*0.1),
            ("Ub", decoder.decode_32bit_float()*0.1),
            ("Uc", decoder.decode_32bit_float()*0.1),
        ]
    )
    return dict


def decode_power(registers):
    decoder = BinaryPayloadDecoder.fromRegisters(
        registers, byteorder=Endian.Big, wordorder=Endian.Big)
    dict = OrderedDict(
        [
            ("ImpEp", decoder.decode_32bit_float()),
        ]
    )
    return dict
