#!/bin/bash

# This script will run during boot to configure BLE settings
# configurations are necessary for BLE functionality

# Print time at which script was run
echo $(date)

# Run this script, and then reboot to enable BATMAN-ADV
DIR=$0
DIR=${DIR::-11}
cd $DIR
DIR=$(pwd)

echo -n Startup Script located at
echo $DIR

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
	echo -e '\E[00;31m'"\033[1mError: This script should run as root\033[0m"
	#exit 1
fi

echo "Startup script is run as root"

# make new empty JSON file
echo "{}" > RSSI.json
echo "non" > ../state

sleep 10
echo $(date)
echo "end of sleep" 


# Modify beacon interval of Raspberry Pi to 10 packets per second
sudo hcitool -i hci0 cmd 0x08 0x0008 1e 02 01 1a 1a ff 4c 00 02 15 e2 c5 6d b5 df fb 48 d2 b0 60 d0 f5 a7 10 96 e0 00 00 00 00 c5 00 00 00 00 00 00 00 00 00 00 00 00 00
sudo hcitool -i hci0 cmd 0x08 0x0006 A0 00 A0 00 03 00 00 00 00 00 00 00 00 07 00
sudo hcitool -i hci0 cmd 0x08 0x000a 01

# Start BLE peripheral server
./ble_per.py

