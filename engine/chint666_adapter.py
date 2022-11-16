import logging
from collections import OrderedDict
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from api.web_app import update_electricity, update_power

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
            ("em_Uab", decoder.decode_32bit_float()*0.1),
            ("em_Ubc", decoder.decode_32bit_float()*0.1),
            ("em_Uca", decoder.decode_32bit_float()*0.1),
            ("em_Ua", decoder.decode_32bit_float()*0.1),
            ("em_Ub", decoder.decode_32bit_float()*0.1),
            ("em_Uc", decoder.decode_32bit_float()*0.1),
            ("em_Ia", decoder.decode_32bit_float()*0.001),
            ("em_Ib", decoder.decode_32bit_float()*0.001),
            ("em_Ic", decoder.decode_32bit_float()*0.001),
            ("em_Pt", decoder.decode_32bit_float()*0.1),
            ("em_Pa", decoder.decode_32bit_float()*0.1),
            ("em_Pb", decoder.decode_32bit_float()*0.1),
            ("em_Pc", decoder.decode_32bit_float()*0.1),
            ("em_Qt", decoder.decode_32bit_float()*0.1),
            ("em_Qa", decoder.decode_32bit_float()*0.1),
            ("em_Qb", decoder.decode_32bit_float()*0.1),
            ("em_Qc", decoder.decode_32bit_float()*0.1),
        ]
    )
    decoder.skip_bytes(8)
    dict["em_PFt"] = decoder.decode_32bit_float()*0.001
    dict["em_PFa"] = decoder.decode_32bit_float()*0.001
    dict["em_PFb"] = decoder.decode_32bit_float()*0.001
    dict["em_PFc"] = decoder.decode_32bit_float()*0.001
    decoder.skip_bytes(18)
    dict["em_Freq"] = decoder.decode_32bit_float()*0.01

    return dict


def decode_power(registers):
    decoder = BinaryPayloadDecoder.fromRegisters(
        registers, byteorder=Endian.Big, wordorder=Endian.Big)
    dict = OrderedDict()
    dict["em_ImpEp"] = decoder.decode_32bit_float()
    decoder.skip_bytes(8)
    dict["em_ExpEp"] = decoder.decode_32bit_float()
    decoder.skip_bytes(8)
    dict["em_Q1Eq"] = decoder.decode_32bit_float()
    decoder.skip_bytes(8)
    dict["em_Q2Eq"] = decoder.decode_32bit_float()
    decoder.skip_bytes(8)
    dict["em_Q3Eq"] = decoder.decode_32bit_float()
    decoder.skip_bytes(8)
    dict["em_Q4Eq"] = decoder.decode_32bit_float()

    return dict
