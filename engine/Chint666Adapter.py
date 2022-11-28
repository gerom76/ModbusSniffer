import logging
from collections import OrderedDict
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from api.web_app import update_smart_meter_legacy, update_statistics

logger = logging.getLogger()

class Chint666TunedAdapter:
    queryCounter = 0

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def __init__(self, decoder):
        self.decoder = decoder

    def decode_electricity(self):
        self.decoder.reset()
        dict = OrderedDict(
            [
                ("em_Uab", self.decoder.decode_32bit_float()*0.1), # 2000H -> 8192
                ("em_Ubc", self.decoder.decode_32bit_float()*0.1), # 2002H
                ("em_Uca", self.decoder.decode_32bit_float()*0.1), # 2004H
                ("em_Ua", self.decoder.decode_32bit_float()*0.1),
                ("em_Ub", self.decoder.decode_32bit_float()*0.1),
                ("em_Uc", self.decoder.decode_32bit_float()*0.1),
                ("em_Ia", self.decoder.decode_32bit_float()*0.001),
                ("em_Ib", self.decoder.decode_32bit_float()*0.001),
                ("em_Ic", self.decoder.decode_32bit_float()*0.001),
                ("em_Pt", self.decoder.decode_32bit_float()*0.1),
                ("em_Pa", self.decoder.decode_32bit_float()*0.1),
                ("em_Pb", self.decoder.decode_32bit_float()*0.1),
                ("em_Pc", self.decoder.decode_32bit_float()*0.1),
                ("em_Qt", self.decoder.decode_32bit_float()*0.1),
                ("em_Qa", self.decoder.decode_32bit_float()*0.1),
                ("em_Qb", self.decoder.decode_32bit_float()*0.1),
                ("em_Qc", self.decoder.decode_32bit_float()*0.1), # 2020H -> 8224
            ]
        )
        # 202AH -> 8234
        self.decoder.skip_bytes(16)
        dict["em_PFt"] = self.decoder.decode_32bit_float()*0.001 # regs[17]*0.001
        dict["em_PFa"] = self.decoder.decode_32bit_float()*0.001 # regs[18]*0.001
        dict["em_PFb"] = self.decoder.decode_32bit_float()*0.001 # regs[19]*0.001
        # 2030H -> 8240
        dict["em_PFc"] = self.decoder.decode_32bit_float()*0.001 # regs[20]*0.001

        # 2044H -> 8260
        self.decoder.skip_bytes(36)
        dict["em_Freq"] = self.decoder.decode_32bit_float()*0.01
        self.decoder.reset()
        return dict


    def decode_power(self):
        self.decoder.reset()
        dict = OrderedDict()
        # 101EH -> 4126
        dict["em_ImpEp"] = self.decoder.decode_32bit_float()
        # 1028H -> 4136
        self.decoder.skip_bytes(16)
        dict["em_ExpEp"] = self.decoder.decode_32bit_float()
        # 1032H -> 4146
        self.decoder.skip_bytes(16)
        dict["em_Q1Eq"] = self.decoder.decode_32bit_float()
        # 103CH -> 4156
        self.decoder.skip_bytes(16)
        dict["em_Q2Eq"] = self.decoder.decode_32bit_float()
        # 1046H -> 4166
        self.decoder.skip_bytes(16)
        dict["em_Q3Eq"] = self.decoder.decode_32bit_float()
        # 1050H -> 4176
        self.decoder.skip_bytes(16)
        dict["em_Q4Eq"] = self.decoder.decode_32bit_float()
        self.decoder.reset()
        return dict

class Chint666LegacyAdapter:
    queryCounter = 0

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def log_decode_32bit_float(self, decoder: BinaryPayloadDecoder, count):
        decoder.reset()
        for i in range(count):
            logger.debug(f'{i}: {decoder.decode_32bit_float()},')
        decoder.reset()

    def decode_range_32bit_float(self, decoder: BinaryPayloadDecoder, count):
        decoder.reset()
        data=[]
        for i in range(count):
            data.append(decoder.decode_32bit_float())
        decoder.reset()
        return data

    def decode_electricity(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.Big, wordorder=Endian.Big)
        regs = self.decode_range_32bit_float(decoder, int(len(registers)/2))
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
        dict["em_PFt"] = decoder.decode_32bit_float()*0.001 # regs[17]*0.001
        dict["em_PFa"] = decoder.decode_32bit_float()*0.001 # regs[18]*0.001
        dict["em_PFb"] = decoder.decode_32bit_float()*0.001 # regs[19]*0.001
        # 2030H -> 8240
        dict["em_PFc"] = decoder.decode_32bit_float()*0.001 # regs[20]*0.001

        # 2044H -> 8260
        dict["em_Freq"] = regs[34]*0.01   # decoder.decode_32bit_float()*0.01

        # self.log_decode_32bit_float(decoder,41)
        return dict

    def decode_power(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.Big, wordorder=Endian.Big)
        
        regs = self.decode_range_32bit_float(decoder, int(len(registers)/2))
        dict = OrderedDict()
        # 101EH -> 4126
        dict["em_ImpEp"] = decoder.decode_32bit_float()
        
        # decoder.skip_bytes(5)
        # 1028H -> 4136
        dict["em_ExpEp"] = regs[5]  # decoder.decode_32bit_float()
        
        # decoder.skip_bytes(5)
        # 1032H -> 4146
        dict["em_Q1Eq"] = regs[10]  # decoder.decode_32bit_float()
        
        #decoder.skip_bytes(5)
        # 103CH -> 4156
        dict["em_Q2Eq"] = regs[15]  # decoder.decode_32bit_float()
        
        # decoder.skip_bytes(5)
        # 1046H -> 4166
        dict["em_Q3Eq"] = regs[20]  # decoder.decode_32bit_float()
        
        # decoder.skip_bytes(5)
        # 1050H -> 4176
        dict["em_Q4Eq"] = regs[25]  # decoder.decode_32bit_float()

        # self.log_decode_32bit_float(decoder,30)
        return dict
