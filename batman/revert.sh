#!/bin/bash

# Run this script and then reboot to revert settings for BATMAN-ADV
DIR=$0
DIR=${DIR::-9}
cd $DIR
DIR=$(pwd)

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
	echo -e '\E[00;31m'"\033[1mError: This script should run as root\033[0m"
	exit 1
fi

# Undo changes in /etc/rc.local
sudo -u pi echo " " > $DIR/temp
sudo grep -v "start-batman-adv.sh" /etc/rc.local > $DIR/temp && sudo mv $DIR/temp /etc/rc.local
echo -en '\E[00;32m'"[*] "
tput sgr0
echo " Modified rc.local. Removed 2 lines."

# Undo changes in /etc/dhcpcd.conf
sudo -u pi echo " " > $DIR/temp
sudo grep -v "denyinterfaces wlan0" /etc/dhcpcd.conf > $DIR/temp && sudo mv $DIR/temp /etc/dhcpcd.conf
echo -en '\E[00;32m'"[*] "
tput sgr0
echo " Modified dhcpcd.local. Removed 1 line. <denyinterfaces wlan0>" 

sudo rm /etc/network/interfaces.d/wlan0
echo -en '\E[00;32m'"[*] "
tput sgr0
echo -n " Removed wlan0 interface. Removed 1 file at "
echo -e '\E[00;36m'"/etc/network/interfaces.d"
tput sgr0
echo " "
echo "Reboot the controller for changes to take effect."

