#!/bin/sh
rm logs/modbus_sniffer.log
# Cheap USB RS485 dongle
# python modbus_sniffer.py /dev/ttyUSB0 9600 1 generic
# Waveshare USB RS485 B dongle
python modbus_sniffer.py /dev/ttyACM1 9600 1 optimized
