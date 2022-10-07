#!/bin/bash

# print time at which script was run
echo $(date)

print_interface=$(ifconfig bat0 | grep "inet ")
echo $print_interface

#while [[ -z $IP_connected ]] ; do
	# repeat until bat0 is automatically assigned an IP with APIPA
	#sleep 1
	#IP_connected=$(ifconfig bat0 | grep "inet ")
	#echo Checking for Automatic Private Assigned IP Address: $IP_connected
#done

# Get the static IP address stored in /home/pi/info.add
print_static_IP=$(cat /home/pi/FYP-Viv-Sxw/info.add | grep 192.168.1.)
sudo ifconfig $print_static_IP

while [[ 0 -eq 0 ]] ; do
	# At this point, the script should have attempted to assign an IP via ipconfig
	# TODO: check if the IP has been successfully assigned to the bat0 interface 
	sleep 5
	grep_IP=$(ifconfig bat0 | grep "192.168.1.")
	echo Grepping IP of bat0 interface: $grep_IP

	if [[ -z $grep_IP ]] ; then
		echo -en "\e[1;31m[!] Error: \e[0m"
		tput sgr0
		echo IP not assigned properly, retrying ...
		print_static_IP=$(cat /home/pi/FYP-Viv-Sxw/info.add | grep 192.168.1.)
		sudo ifconfig $print_static_IP
	else
		echo -en "\e[1;32m[*]\e[0m"
		tput sgr0
		echo " IP address has been assigned successfully, exiting ..."
		break
	fi
done

