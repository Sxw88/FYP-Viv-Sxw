#!/bin/bash

# Run this script, and then reboot to enable BATMAN-ADV
DIR=$0
DIR=${DIR::-19}
cd $DIR
DIR=$(pwd)

if [[ $EUID -ne 0 ]]; then
	echo -e '\E[00;31m'"\033[1mError: This script should run as root\033[0m"
	exit 1
fi

echo $(date)
echo "Starting BATMAN-ADV:"

# batman-adv interface to use
sudo batctl if add wlan0
sudo ifconfig bat0 mtu 1468

# Tell batman-adv this is a gateway client
sudo batctl gw_mode client

# Activates batman-adv interfaces
sudo ifconfig wlan0 up
sudo ifconfig bat0 up

# Assign static IP address
sudo /home/pi/FYP-Viv-Sxw/batman/get-IP-static.sh
