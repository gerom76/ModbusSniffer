# ModbusSniffer
Modbus RTU packet sniffer

Wrapper around pymodbus to print all packets on bus from either slave or master.
Useful for sniffing packets between two devices to ensure correct operation.

Simple command line tool that prints results to the terminal.

/bin/python3.9 /home/adminus/source/ContribRepos/ModbusSniffer/modbus_sniffer.py /dev/ttyUSB0
