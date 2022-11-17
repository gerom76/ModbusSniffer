import logging
from collections import OrderedDict
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from api.web_app import update_electricity, update_power

logger = logging.getLogger()

def process_meter_response(msg):
    try:
        data = ' '.join([hex(i) for i in msg.registers])
        count = len(msg.registers)
        logger.info(f'Processing meter: {msg} ({count}) \n{data}\n{msg.registers}')
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
            ("em_Uab", decoder.decode_32bit_float()*0.1), # 2000H -> 8192
            ("em_Ubc", decoder.decode_32bit_float()*0.1), # 2002H
            ("em_Uca", decoder.decode_32bit_float()*0.1), # 2004H
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
            ("em_Qc", decoder.decode_32bit_float()*0.1), # 2020H -> 8224
        ]
    )
    decoder.skip_bytes(16)
    
    # 202AH -> 8234
    dict["em_PFt"] = decoder.decode_32bit_float()*0.001
    dict["em_PFa"] = decoder.decode_32bit_float()*0.001
    dict["em_PFb"] = decoder.decode_32bit_float()*0.001
    
    # 2030H -> 8240
    dict["em_PFc"] = decoder.decode_32bit_float()*0.001
    decoder.skip_bytes(20)
    
    # 2044H -> 8260
    dict["em_Freq"] = decoder.decode_32bit_float()*0.01

    return dict


def decode_power(registers):
    decoder = BinaryPayloadDecoder.fromRegisters(
        registers, byteorder=Endian.Big, wordorder=Endian.Big)
    dict = OrderedDict()
    # 101EH -> 4126
    dict["em_ImpEp"] = decoder.decode_32bit_float()
    decoder.skip_bytes(10)
    
    # 1028H -> 4136
    dict["em_ExpEp"] = decoder.decode_32bit_float()
    decoder.skip_bytes(10)
    
    # 1032H -> 4146
    dict["em_Q1Eq"] = decoder.decode_32bit_float()
    decoder.skip_bytes(10)
    
    # 103CH -> 4156
    dict["em_Q2Eq"] = decoder.decode_32bit_float()
    decoder.skip_bytes(10)
    
    # 1046H -> 4166
    dict["em_Q3Eq"] = decoder.decode_32bit_float()
    decoder.skip_bytes(10)
    
    # 1050H -> 4176
    dict["em_Q4Eq"] = decoder.decode_32bit_float()

    return dict
