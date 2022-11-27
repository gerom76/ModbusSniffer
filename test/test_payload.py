"""Payload Utilities Test Fixture.

This fixture tests the functionality of the payload
utilities.

* PayloadBuilder
* PayloadDecoder
"""
import logging
import unittest

from pymodbus.constants import Endian
from pymodbus.exceptions import ParameterException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

from engine.serial_snooper import SerialSnooper
logger = logging.getLogger()

# ---------------------------------------------------------------------------#
#  Fixture
# ---------------------------------------------------------------------------#


class ModbusPayloadUtilityTests(unittest.TestCase):
    """Modbus payload utility tests."""

    # ----------------------------------------------------------------------- #
    # Setup/TearDown
    # ----------------------------------------------------------------------- #

    def setUp(self):
        """Initialize the test environment and builds request/result encoding pairs."""
        self.little_endian_payload = (
            b"\x01\x02\x00\x03\x00\x00\x00\x04\x00\x00\x00\x00"
            b"\x00\x00\x00\xff\xfe\xff\xfd\xff\xff\xff\xfc\xff"
            b"\xff\xff\xff\xff\xff\xff\x00\x00\xa0\x3f\x00\x00"
            b"\x00\x00\x00\x00\x19\x40\x01\x00\x74\x65\x73\x74"
            b"\x11"
        )

        self.big_endian_payload = (
            b"\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00"
            b"\x00\x00\x04\xff\xff\xfe\xff\xff\xff\xfd\xff\xff"
            b"\xff\xff\xff\xff\xff\xfc\x3f\xa0\x00\x00\x40\x19"
            b"\x00\x00\x00\x00\x00\x00\x00\x01\x74\x65\x73\x74"
            b"\x11"
        )

        self.bitstring = [True, False, False, False, True, False, False, False]

    def tearDown(self):
        """Clean up the test environment"""

    # ----------------------------------------------------------------------- #
    # Payload Builder Tests
    # ----------------------------------------------------------------------- #

    def test_little_endian_payload_builder(self):
        """Test basic bit message encoding/decoding"""
        builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Little)
        builder.add_8bit_uint(1)
        builder.add_16bit_uint(2)
        builder.add_32bit_uint(3)
        builder.add_64bit_uint(4)
        builder.add_8bit_int(-1)
        builder.add_16bit_int(-2)
        builder.add_32bit_int(-3)
        builder.add_64bit_int(-4)
        builder.add_32bit_float(1.25)
        builder.add_64bit_float(6.25)
        builder.add_16bit_uint(1)  # placeholder
        builder.add_string(b"test")
        builder.add_bits(self.bitstring)
        self.assertEqual(self.little_endian_payload, builder.to_string())

    def test_big_endian_payload_builder(self):
        """Test basic bit message encoding/decoding"""
        builder = BinaryPayloadBuilder(byteorder=Endian.Big)
        builder.add_8bit_uint(1)
        builder.add_16bit_uint(2)
        builder.add_32bit_uint(3)
        builder.add_64bit_uint(4)
        builder.add_8bit_int(-1)
        builder.add_16bit_int(-2)
        builder.add_32bit_int(-3)
        builder.add_64bit_int(-4)
        builder.add_32bit_float(1.25)
        builder.add_64bit_float(6.25)
        builder.add_16bit_uint(1)  # placeholder
        builder.add_string("test")
        builder.add_bits(self.bitstring)
        self.assertEqual(self.big_endian_payload, builder.to_string())

    def test_payload_builder_reset(self):
        """Test basic bit message encoding/decoding"""
        builder = BinaryPayloadBuilder()
        builder.add_8bit_uint(0x12)
        builder.add_8bit_uint(0x34)
        builder.add_8bit_uint(0x56)
        builder.add_8bit_uint(0x78)
        self.assertEqual(b"\x12\x34\x56\x78", builder.to_string())
        self.assertEqual([b"\x12\x34", b"\x56\x78"], builder.build())
        builder.reset()
        self.assertEqual(b"", builder.to_string())
        self.assertEqual([], builder.build())

    def test_payload_builder_with_raw_payload(self):
        """Test basic bit message encoding/decoding"""
        _coils1 = [
            False,
            False,
            True,
            True,
            False,
            True,
            False,
            False,
            False,
            False,
            False,
            True,
            False,
            False,
            True,
            False,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            True,
            False,
            True,
            False,
            True,
            True,
            False,
        ]
        _coils2 = [
            False,
            False,
            False,
            True,
            False,
            False,
            True,
            False,
            False,
            False,
            True,
            True,
            False,
            True,
            False,
            False,
            False,
            True,
            False,
            True,
            False,
            True,
            True,
            False,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
        ]

        builder = BinaryPayloadBuilder(
            [b"\x12", b"\x34", b"\x56", b"\x78"], repack=True
        )
        self.assertEqual(b"\x12\x34\x56\x78", builder.to_string())
        self.assertEqual([13330, 30806], builder.to_registers())
        coils = builder.to_coils()
        self.assertEqual(_coils1, coils)

        builder = BinaryPayloadBuilder(
            [b"\x12", b"\x34", b"\x56", b"\x78"], byteorder=Endian.Big
        )
        self.assertEqual(b"\x12\x34\x56\x78", builder.to_string())
        self.assertEqual([4660, 22136], builder.to_registers())
        self.assertEqual("\x12\x34\x56\x78", str(builder))
        coils = builder.to_coils()
        self.assertEqual(_coils2, coils)

    # ----------------------------------------------------------------------- #
    # Payload Decoder Tests
    # ----------------------------------------------------------------------- #

    def test_little_endian_payload_decoder(self):
        """Test basic bit message encoding/decoding"""
        decoder = BinaryPayloadDecoder(
            self.little_endian_payload, byteorder=Endian.Little, wordorder=Endian.Little
        )
        self.assertEqual(1, decoder.decode_8bit_uint())
        self.assertEqual(2, decoder.decode_16bit_uint())
        self.assertEqual(3, decoder.decode_32bit_uint())
        self.assertEqual(4, decoder.decode_64bit_uint())
        self.assertEqual(-1, decoder.decode_8bit_int())
        self.assertEqual(-2, decoder.decode_16bit_int())
        self.assertEqual(-3, decoder.decode_32bit_int())
        self.assertEqual(-4, decoder.decode_64bit_int())
        self.assertEqual(1.25, decoder.decode_32bit_float())
        self.assertEqual(6.25, decoder.decode_64bit_float())
        self.assertEqual(None, decoder.skip_bytes(2))
        self.assertEqual("test", decoder.decode_string(4).decode())
        self.assertEqual(self.bitstring, decoder.decode_bits())

    def test_big_endian_payload_decoder(self):
        """Test basic bit message encoding/decoding"""
        decoder = BinaryPayloadDecoder(self.big_endian_payload, byteorder=Endian.Big)
        self.assertEqual(1, decoder.decode_8bit_uint())
        self.assertEqual(2, decoder.decode_16bit_uint())
        self.assertEqual(3, decoder.decode_32bit_uint())
        self.assertEqual(4, decoder.decode_64bit_uint())
        self.assertEqual(-1, decoder.decode_8bit_int())
        self.assertEqual(-2, decoder.decode_16bit_int())
        self.assertEqual(-3, decoder.decode_32bit_int())
        self.assertEqual(-4, decoder.decode_64bit_int())
        self.assertEqual(1.25, decoder.decode_32bit_float())
        self.assertEqual(6.25, decoder.decode_64bit_float())
        self.assertEqual(None, decoder.skip_bytes(2))
        self.assertEqual(b"test", decoder.decode_string(4))
        self.assertEqual(self.bitstring, decoder.decode_bits())

    def test_payload_decoder_reset(self):
        """Test the payload decoder reset functionality"""
        decoder = BinaryPayloadDecoder(b"\x12\x34")
        self.assertEqual(0x12, decoder.decode_8bit_uint())
        self.assertEqual(0x34, decoder.decode_8bit_uint())
        decoder.reset()
        self.assertEqual(0x3412, decoder.decode_16bit_uint())

    def test_payload_decoder_register_factory(self):
        """Test the payload decoder reset functionality"""
        payload = [1, 2, 3, 4]
        decoder = BinaryPayloadDecoder.fromRegisters(payload, byteorder=Endian.Little)
        encoded = b"\x00\x01\x00\x02\x00\x03\x00\x04"
        self.assertEqual(encoded, decoder.decode_string(8))

        decoder = BinaryPayloadDecoder.fromRegisters(payload, byteorder=Endian.Big)
        encoded = b"\x00\x01\x00\x02\x00\x03\x00\x04"
        self.assertEqual(encoded, decoder.decode_string(8))

        self.assertRaises(
            ParameterException, lambda: BinaryPayloadDecoder.fromRegisters("abcd")
        )

    def test_payload_decoder_coil_factory(self):
        """Test the payload decoder reset functionality"""
        payload = [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]
        decoder = BinaryPayloadDecoder.fromCoils(payload, byteorder=Endian.Little)
        encoded = b"\x88\x11"
        self.assertEqual(encoded, decoder.decode_string(2))

        decoder = BinaryPayloadDecoder.fromCoils(payload, byteorder=Endian.Big)
        encoded = b"\x88\x11"
        self.assertEqual(encoded, decoder.decode_string(2))

        self.assertRaises(
            ParameterException, lambda: BinaryPayloadDecoder.fromCoils("abcd")
        )
        
    def test_payload_decoder_raw_request1(self):
        """Test the request 1 decoder functionality"""
        request1 = '0104200000527A37'
        print(request1)
        # TODO: wrap into request_decode_header function
        message = bytearray.fromhex(request1)
        print(message)
        slave_adr, func_code, start_address, quantity = SerialSnooper.decode_request_message(message)
        self.assertEqual(slave_adr, 1)
        self.assertEqual(func_code, 4)
        self.assertEqual(start_address, '2000')
        self.assertEqual(quantity, '0052')
        is_valid = SerialSnooper.check_message(message)
        self.assertEqual(is_valid, True)

    def test_payload_decoder_raw_response1(self):
        """Test the response 1 decoder functionality"""
        response = '0104A4458218004582180045821800451640004516400045164000415000004130000041400000C1300000C130000041100000C110000041A8000041900000C180000041980000429A000041C8000041C8000041C80000C3110000C3DC000043B38000C3B780004493C0004539D000448D0000000000000000000000000000000000000000000000000000459C30004110000047693B00000000000000000000000000000000002CF7'
        print(response)
        # TODO: wrap into response_decode_header function
        message = bytearray.fromhex(response)
        print(message)
        slave_adr, func_code, byte_count = SerialSnooper.decode_response_message(message)
        self.assertEqual(slave_adr, 1)
        self.assertEqual(func_code, 4)
        self.assertEqual(byte_count, 164)
        is_valid = SerialSnooper.check_message(message)
        self.assertEqual(is_valid, True)
        # x = [b"\x12", b"\x34", b"\x56", b"\x78"] 
        # bytes(data[0:1]) ->  b'\x01'
        # bytes(data[1:2]) -> b'\x04'
        
        payload = SerialSnooper.extract_payload(message, byte_count)
        decoder = SerialSnooper.load_decoder(payload)
        SerialSnooper.log_registry(message, byte_count, decoder)
        
        # decoder.reset()
        # for i in range(int(byte_count/4)):
        #     print(f'{i}: {decoder.decode_32bit_float()},')
        # decoder.reset()
        
        # Uab
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 4163)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 4163)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 4163)
        # Ua
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 2404)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 2404)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 2404)
        # Ia
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 13)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 11)
        # Ic
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 12)
        # Pt
        value = decoder.decode_32bit_float()
        self.assertEqual(value, -11)
        # Pa
        value = decoder.decode_32bit_float()
        self.assertEqual(value, -11)
        # Pb
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 9)
        # Pc
        value = decoder.decode_32bit_float()
        self.assertEqual(value, -9)
        # Qt
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 21)
        # Qa
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 18)
        # Qb
        value = decoder.decode_32bit_float()
        self.assertEqual(value, -16)
        # Qc
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 19)
        # PFt
        decoder.skip_bytes(16)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, -145)
        # PFa
        value = decoder.decode_32bit_float()
        self.assertEqual(value, -440)
        # PFb
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 359)
        # PFc
        value = decoder.decode_32bit_float()
        self.assertEqual(value, -367)
        # Freq
        decoder.skip_bytes(36)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 4998)
        
    def test_payload_decoder_raw_request2(self):
        """Test the request 2 decoder functionality"""
        request = '0104101E003C94DD'
        print(request)
        message = bytearray.fromhex(request)
        print(message)
        slave_adr, func_code, start_address, quantity = SerialSnooper.decode_request_message(message)
        self.assertEqual(slave_adr, 1)
        self.assertEqual(func_code, 4)
        self.assertEqual(start_address, '101e')
        self.assertEqual(quantity, '003c')
        is_valid = SerialSnooper.check_message(message)
        self.assertEqual(is_valid, True)
        
    def test_payload_decoder_raw_response2(self):
        """Test the response 2 decoder functionality"""
        response = '010478415170A4415170A400000000000000000000000041251EB841251EB8000000000000000000000000400AE148400AE148000000000000000000000000422B51EC422B51EC0000000000000000000000003F3333333F3333330000000000000000000000003F0F5C293F0F5C290000000000000000000000004FF2'
        print(response)
        message = bytearray.fromhex(response)
        print(message)
        slave_adr, func_code, byte_count = SerialSnooper.decode_response_message(message)
        self.assertEqual(slave_adr, 1)
        self.assertEqual(func_code, 4)
        self.assertEqual(byte_count, 120)
        is_valid = SerialSnooper.check_message(message)
        self.assertEqual(is_valid, True)
        
        payload = SerialSnooper.extract_payload(message, byte_count)
        decoder = SerialSnooper.load_decoder(payload)
        SerialSnooper.log_registry(message, byte_count, decoder)
        
        # decoder.reset()
        # for i in range(int(byte_count/4)):
        #     print(f'{i}: {decoder.decode_32bit_float()},')
        # decoder.reset()
        
        #ImpEp
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 13.09000015258789)
        #ExpEp
        decoder.skip_bytes(16)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 10.319999694824219)
        #Q1Eq
        decoder.skip_bytes(16)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 2.1700000762939453)
        decoder.skip_bytes(16)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 42.83000183105469)
        decoder.skip_bytes(16)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 0.699999988079071)
        #Q4Eq
        decoder.skip_bytes(16)
        value = decoder.decode_32bit_float()
        self.assertEqual(value, 0.5600000023841858)
