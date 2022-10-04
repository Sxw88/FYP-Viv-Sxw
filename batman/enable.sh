#!/bin/bash

# Run this script, and then reboot to enable BATMAN-ADV
DIR=$0
DIR=${DIR::-9}
cd $DIR
DIR=$(pwd)

if [[ $EUID -ne 0 ]]; then
	echo -e '\E[00;31m'"\033[1mError: This script should run as root\033[0m"
	exit 1
fi

# One-liner to add cronjob which starts the script <start-batman-adv.sh> 20 seconds after rebooting
echo -e "$(sudo crontab -u root -l)\n@reboot sleep 20 && /home/pi/FYP-Viv-Sxw/batman/start-batman-adv.sh > /home/pi/FYP-Viv-Sxw/batman/batman.log" | sudo crontab -u root -
echo -en '\E[00;32m'"[*] "
tput sgr0
echo "Adding cron job..."


# Create wlan0 network interface
sudo cp $DIR/wlan0 /etc/network/interfaces.d/wlan0
echo -en '\E[00;32m'"[*] "
tput sgr0
echo -n "Created wlan0 interface at "
echo -e '\E[00;36m'"/etc/network/interfaces.d/wlan0 "
tput sgr0

# Append batman-adv to list of kernel modules, so that it is loaded at boot
sudo -u pi echo " " > $DIR/temp
sudo grep -v "batman-adv" /etc/modules > $DIR/temp && sudo mv $DIR/temp /etc/modules
sudo echo 'batman-adv' >> /etc/modules 
echo -en '\E[00;32m'"[*] "
tput sgr0
echo -n "Appended to  "
echo -en '\E[00;36m'"/etc/modules "
tput sgr0
echo "at line: "
echo "  $(grep -n 'batman-adv' /etc/modules)"

#ensure DHCP process does not manage wireless LAN interface
sudo -u pi echo " " > $DIR/temp
sudo grep -v "denyinterfaces wlan0" /etc/dhcpcd.conf > $DIR/temp && sudo mv $DIR/temp /etc/dhcpcd.conf
sudo echo 'denyinterfaces wlan0' >> /etc/dhcpcd.conf
sudo echo 'noipv4ll' >> /etc/dhcpcd.conf
echo -en '\E[00;32m'"[*] "
tput sgr0
echo -n "Appended to  "
echo -en '\E[00;36m'"/etc/dhcpcd.conf "
tput sgr0
echo "at lines: "
echo "  $(grep -n 'denyinterfaces wlan0' /etc/dhcpcd.conf)"
echo "  $(grep -n 'noipv4ll' /etc/dhcpcd.conf)"

sudo reboot

#run start-batman-adv.sh
sudo ifconfig wlan0 down
sudo ./start-batman-adv.sh | tee ./batman.log 

#restart services
sudo service dhcpcd restart
sudo iwconfig wlan0 mode Ad-Hoc
sudo service networking restart
