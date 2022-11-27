#!/bin/sh
rm logs/modbus_sniffer.log
python modbus_sniffer.py /dev/ttyUSB0 9600 1 generic