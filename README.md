# ModbusSniffer
Modbus RTU packet sniffer

Wrapper around pymodbus to print all packets on bus from either slave or master.
Useful for sniffing packets between two devices to ensure correct operation.

Simple command line tool that prints results to the terminal.
----------------------------------------------------
sudo pip install -r requirements.txt    

----------------------------------------------------
WSL env and RS485 USB dongle:

powershell:
usbipd list
usbipd wsl attach --busid 2-11

linux:
sudo chmod 666 /dev/ttyUSB0

------------------------------------------------------
https://www.waveshare.com/wiki/USB_TO_RS485_(B)

-----------------------------------------------------
run in background:
cd ~/source/ContribRepos/ModbusSniffer
./modbus-sniffer.sh &
or
python modbus_sniffer.py /dev/ttyUSB0 9600 1 generic



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
sudo cp -r ~/source/ContribRepos/ModbusSniffer/* /srv/modbus-sniffer/

sudo -u homeassistant -H -s
cd /srv/modbus-sniffer
python3.10 -m venv .
source bin/activate
pip install -r requirements.txt

sudo service modbus-sniffer-daemon install

sudo service modbus-sniffer-daemon start
sudo service modbus-sniffer-daemon stop
-----------------------------------------------------
systemctl:

https://community.home-assistant.io/t/autostart-using-systemd/199497

sudo systemctl --system daemon-reload
sudo systemctl enable modbus-sniffer@homeassistant
sudo systemctl start modbus-sniffer@homeassistant

sudo systemctl status modbus-sniffer@homeassistant

sudo systemctl restart modbus-sniffer@homeassistant


sudo journalctl -f -u modbus-sniffer@homeassistant | grep -i 'error'


-------------------------------------------------------

Start Homassistant service:

sudo service hass-daemon start


----------------------------------------------------
cd /srv/modbus-sniffer/ 
python3.9 -m venv . && source bin/activate && 
python modbus_sniffer.py /dev/ttyACM0 9600 1 optimized


-------------------
https://msadowski.github.io/linux-static-port/
99-com.rules

KERNEL=="ttyACM0", ATTRS{product}=="SONOFF Zigbee 3.0 USB Dongle Plus V2"

KERNEL=="ttyACM1", ATTRS{product}=="USB Single Serial", ATTRS{serial}=="54D2072038"

