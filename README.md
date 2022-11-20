# ModbusSniffer
Modbus RTU packet sniffer

Wrapper around pymodbus to print all packets on bus from either slave or master.
Useful for sniffing packets between two devices to ensure correct operation.

Simple command line tool that prints results to the terminal.

----------------------------------------------------
WSL env and RS485 USB dongle:

powershell:
usbipd list
usbipd wsl attach --busid 2-11

linux:
sudo chmod 666 /dev/ttyUSB0


-----------------------------------------------------
run in background:
cd ~/source/ContribRepos/ModbusSniffer
./run_sniffer.sh &

to terminate use:
ps
kill
-----------------------------------------------------
Install daemon:

sudo apt install daemonize
sudo cp docs/daemon/modbus-sniffer-daemon /etc/init.d/
sudo chmod +x /etc/init.d/modbus-sniffer-daemon
sudo mkdir /var/log/modbus-sniffer
sudo cp docs/daemon/modbus-sniffer._log /var/log/modbus-sniffer/modbus-sniffer.log

sudo service modbus-sniffer install

sudo service modbus-sniffer start
-----------------------------------------------------

Start Homassistant service:

sudo service hass-daemon start


----------------------------------------------------
/bin/python3.9 /home/adminus/source/ContribRepos/ModbusSniffer/modbus_sniffer.py /dev/ttyUSB0



