#!/bin/bash

#initialisation script, run this after cloning the GitHub repo
DIR=$0
DIR=${DIR::-7}
cd $DIR
DIR=$(pwd)

#functions
function verify_pkg {
  local REQUIRED_PKG=$1
	local PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
	local input="x"
	
	echo -n "[*] Checking for $REQUIRED_PKG : "
	echo -e '\E[00;32m'"$PKG_OK"
	tput sgr0	
	#if package is not already installed
	if [ "" = "$PKG_OK" ]; then 
	  echo -en '\E[00;33m'"\033[1m[*] \033[0m"
		tput sgr0	
	  echo "$REQUIRED_PKG not found. Setting up $REQUIRED_PKG."
	  sudo apt-get --yes install $REQUIRED_PKG 

	  #check again for the required package
	  PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
	  echo -en '\E[00;33m'"\033[1m[*] \033[0m"
		tput sgr0	
	  echo -n "Checking again for $REQUIRED_PKG : " 
	  echo -e '\E[00;32m'"$PKG_OK"
		tput sgr0	
	  if [ "" = "$PKG_OK" ]; then 
		echo -en '\E[00;31m'"\033[1m[!] Error: \033[0m"
		tput sgr0	
		echo -n "Installation of $REQUIRED_PKG has failed.."
		#get user input (Y/N) to proceed
		while true
		do
			read -r -p " Proceed? (Y/N)" input
			case $input in
				[yY][eE][sS]|[yY])
					echo "Proceeding with initialisation..."
					break
					;;
				[nN][oO]|[nN])
					echo "Aborting... {missing package $REQUIRED_PKG}"
					exit 3
					;;
				*)
					echo "Invalid Input."
					;;
			esac
		done
	  fi
	fi
}

#checking if the script is being run as root:
if [[ $EUID -ne 0 ]]; then
	echo -e '\E[00;31m'"\033[1mError: This script should run as root\033[0m"
	exit 1
fi

#setting up aliases
echo -en '\E[00;32m'"[*]"
tput sgr0
echo " Setting up aliases..."
offset=0
grep -n "#adding custom aliases" /home/pi/.bashrc | cut -d: -f1 |
	while LOOPER= read -r line ; do
		line=$((line-offset))	
		offset=$((offset+4))
		line_p3=$((line+3))
		var_d="d"
		sudo sed -i "$line,$line_p3$var_d" /home/pi/.bashrc
	done
sudo echo '#adding custom aliases' >> /home/pi/.bashrc
sudo echo "alias fyp=\"cd $DIR\"" >> /home/pi/.bashrc
sudo echo 'alias test="./test.sh"' >> /home/pi/.bashrc
sudo echo "alias stop=\"$DIR/test-scripts/stop.py\"" >> /home/pi/.bashrc

source /home/pi/.bashrc

# Create directory to store the backups
sudo -u pi mkdir -p batman/backup/1

# backup /etc/network/interfaces.d/wlan0 file if it exists
FILE=/etc/network/interfaces.d/wlan0
if test -f "$FILE"; then
	sudo cp /etc/network/interfaces.d/wlan0 ./batman/backup/1/,etc,network,interfaces.d,wlan0
	echo -en '\E[00;32m'"[*]"
	tput sgr0
	echo -n " Discovered wlan0 file... making a backup to "
	echo -e '\E[00;36m'"./batman/backup/1/,etc,network,interfaces.d,wlan0"
	tput sgr0	
else
	echo "[*] wlan0 file not found... Proceeding with the next step."
fi

# backup /etc/dhcpcd.conf file if it exists
FILE=/etc/dhcpcd.conf
if test -f "$FILE"; then
	sudo cp /etc/dhcpcd.conf ./batman/backup/1/,etc,dhcpcd.conf
	echo -en '\E[00;32m'"[*]"
	tput sgr0
	echo -n " Discovered dhcpcd.conf file... making a backup to "
	echo -e '\E[00;36m'"./batman/backup/1/,etc,dhcpcd.conf"
	tput sgr0	
else
	echo -en '\E[00;31m'"\033[1m[!]\033[0m"
	while true
	do
		read -r -p " dhcpcd.conf not found... Proceed? (Y/N)" input
		case $input in
			[yY][eE][sS]|[yY])
				echo "Proceeding with initialisation..."
				break
				;;
			[nN][oO]|[nN])
				echo "Aborting... {dhcpcd.conf not found}"
				exit 2
				;;
			*)
				echo "Invalid Input."
				;;
		esac
	done
fi

# backup /etc/rc.local file if it exists
FILE=/etc/rc.local
if test -f "$FILE"; then
	sudo cp "/etc/rc.local" "./batman/backup/1/,etc,rc.local"
	echo -en '\E[00;32m'"[*]"
	tput sgr0
	echo -n " Discovered rc.local file... making a backup to "
	echo -e '\E[00;36m'"./batman/backup/1/,etc,rc.local"
	tput sgr0	
else
	echo -en '\E[00;31m'"\033[1m[!]\033[0m"
	while true
	do
		read -r -p " rc.local not found... Proceed? (Y/N)" input
		case $input in
			[yY][eE][sS]|[yY])
				echo "Proceeding with initialisation..."
				break
				;;
			[nN][oO]|[nN])
				echo "Aborting... {rc.local not found}"
				exit 2
				;;
			*)
				echo "Invalid Input."
				;;
		esac
	done
fi

# Check if dependencies are installed
verify_pkg "batctl"

# Make executable
echo "[*] Making scripts executable..."
sudo chmod +x $DIR/**/*.sh

# pip install python packages
pip3 install bleak
pip3 install BLE_GATT
