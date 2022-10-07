#!/bin/bash

# NO LONGER USED! 
# get-IP-static.sh is used to assign IP address instead

# print time at which script was run
echo $(date)

target="192.168.1."

while [[ 0 -eq 0 ]] ; do

	IP_connected=$(ifconfig bat0 | grep "inet ")
	echo $IP_connected

	#while [[ -z $IP_connected ]] ; do
		# repeat until bat0 is automatically assigned an IP with APIPA
	#	sleep 1
	#	IP_connected=$(ifconfig bat0 | grep "inet ")
	#	echo Checking for IPV4 address: $IP_connected
	#done
	
	sleep 10

	for a in {1..20} ; do

		target_a=$target$a
		
		ping_rp1=$(ping -c 1 $target_a | grep "bytes from")
		echo Ping Response 1: $ping_rp1
		ping_rp2=$(ping -c 1 $target_a | grep "bytes from")
		echo Ping Response 2: $ping_rp2
		ping_rp3=$(ping -c 1 $target_a | grep "bytes from")
		echo Ping Response 3: $ping_rp3
		ping_rp=$ping_rp1$ping_rp2$ping_rp3

		# check if $ping_rp is empty or not
		if [[ -z $ping_rp ]] 
		then 
			echo -en "\e[1;32m target at $target_a is unreachable\e[0m"
			tput sgr0
			echo "- this IP will be assigned to this machine"
			sudo ifconfig bat0 down
			sudo ifconfig bat0 $target_a
			sudo ifconfig bat0 up
			break
		else
			echo -en "\e[1;33m target at $target_a is reachable, \e[0m"
			echo the search will continue ...
			tput sgr0
		fi

	done
	
	# At this point, the script should have attempted to assign an IP via ipconfig
	# TODO: check if the IP has been successfully assigned to the bat0 interface 
	
	sleep 5
	grep_IP=$(ifconfig bat0 | grep "192.168.1.")
	echo Grepping IP of bat0 interface: $grep_IP
	
	if [[ -z $grep_IP ]] ; then
		echo -en "\e[1;31m[!] Error: \e[0m"
		tput sgr0
		echo IP not assigned properly, retrying ...
	else
		echo -en "\e[1;32m[*]\e[0m"
		tput sgr0
		echo " IP address has been assigned successfully, exiting ..."
		break
	fi

	
done


# FLOW DIAGRAM

#                               ┌────────────────────────────────────────────┐
#                               │                                            │
#                               │                                            │
#                        ┌──────┼─────────────┐                              │
#                        │      │             │                              │
#                        │      │             │ If a ping response           │
#                        │      │             │ is obtained,                 │
#              ┌─────────▼──────▼─────┐       │ x                            │
#              │                      │       │                              │
# start ───────►  ping 192.168.1.x    ├───────┘                              │
#              │                      │                                      │ If IP assignment fails,
#              └─────────┬────────────┘                                      │ (ifconfig grep returns nothing)
#                        │                                                   │   repeat from x = 1
#                        │ If there is no ping response from 192.168.1.x,    │
#                        │ The IP will be assigned to the Pi                 │
#                        │                                                   │
#         ┌──────────────▼──────────────────────┐                            │
#         │                                     │                            │
#         │  sudo ifconfig bat0 192.168.1.x/24  ├────────────────────────────┘
#         │                                     │
#         └──────────────┬──────────────────────┘
#                        │
#                        │
#                        ▼
#           IP address has been assigned!	
