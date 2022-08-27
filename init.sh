#!/bin/bash

#initialisation script, run this after cloning the GitHub repo

#checking if the script is being run as root:
if [[ $EUID -ne 0 ]]; then
	echo -e '\E[00;31m'"\033[1mError: This script should run as root\033[0m"
	exit 1
fi

#setting up aliases
echo -en '\E[00;32m'"[*]"
tput sgr0
echo " Setting up aliases..."
sudo echo '#adding custom aliases' >> /home/pi/.bashrc
sudo echo 'alias fyp="cd /home/pi/FYP-Viv-Sxw"' >> /home/pi/.bashrc
sudo echo 'alias test="./test.sh"' >> /home/pi/.bashrc
sudo echo 'alias stop="/home/pi/test-scripts/stop.py"' >> /home/pi/.bashrc

source /home/pi/.bashrc

###############################################
# make backups of files which will be changed #
###############################################
#create directory to store the backups
mkdir -p backup/batman/1

#backup /etc/network/interfaces.d/wlan0 file if it exists
FILE=/etc/network/interfaces.d/wlan0
if test -f "$FILE"; then
	sudo cp /etc/network/interfaces.d/wlan0 ./backup/batman/1/,etc,network,interfaces.d,wlan0
	echo -en '\E[00;32m'"[*]"
	tput sgr0
	echo -n " Discovered wlan0 file... making a backup to "
	echo -e '\E[00;36m'"/backup/batman-adv/1/,etc,network,interfaces.d,wlan0"
	tput sgr0	
else
	echo "[*] wlan0 file not found... Proceeding with the next step."
fi

#backup /etc/dhcpcd.conf file if it exists
FILE=/etc/dhcpcd.conf
if test -f "$FILE"; then
	sudo cp /etc/dhcpcd.conf ./backup/batman/1/,etc,dhcpcd.conf
	echo -en '\E[00;32m'"[*]"
	tput sgr0
	echo -n " Discovered dhcpcd.conf file... making a backup to "
	echo -e '\E[00;36m'"/backup/batman-adv/1/,etc,dhcpcd.conf"
	tput sgr0	
else
	echo -en '\E[00;31m'"\033[1m[!]\033[0m\n"
	while true
	do
		read -r -p " dhcpcd.conf not found... Proceed? (Y/N)" input
		case $input in
			[yY][eE][sS]|[yY])
				echo "Proceeding with initialisation..."
				;;
			[nN][oO]|[nN])
				echo "Aborting... {dhcpcd.conf not found}"
				;;
			*)
				echo "Invalid Input."
				;;
		esac
	done
fi

#backup /etc/rc.local file if it exists
FILE=/etc/rc.local
if test -f "$FILE"; then
	sudo cp "/etc/rc.local" "./backup/batman/1/,etc,rc.local"
	echo -en '\E[00;32m'"[*]"
	tput sgr0
	echo -n " Discovered rc.local file... making a backup to "
	echo -e '\E[00;36m'"/backup/batman-adv/1/,etc,rc.local"
	tput sgr0	
else
	echo -en '\E[00;31m'"\033[1m[!]\033[0m\n"
	while true
	do
		read -r -p " rc.local not found... Proceed? (Y/N)" input
		case $input in
			[yY][eE][sS]|[yY])
				echo "Proceeding with initialisation..."
				;;
			[nN][oO]|[nN])
				echo "Aborting... {rc.local not found}"
				;;
			*)
				echo "Invalid Input."
				;;
		esac
	done
fi


