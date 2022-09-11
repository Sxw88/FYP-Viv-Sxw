#!/bin/bash

target="192.168.1."

for a in {1..20} ; do

target_a=$target$a

ping_rp1=$(ping -c 1 $target_a | grep "Reply from")
ping_rp2=$(ping -c 1 $target_a | grep "Reply from")
ping_rp3=$(ping -c 1 $target_a | grep "Reply from")
ping_rp=$ping_rp1$ping_rp2$ping_rp3

# check if $ping_rp is empty or not
#if [[ -z $ping_rp1 && -z $ping_rp2 && -z $ping_rp3 ]] 
if [[ -z $ping_rp ]] 
then 
	echo -en "\e[1;32m target at $target_a is unreachable\e[0m"
	tput sgr0
	echo "- this IP will be assigned to this machine"
	sudo ifconfig bat0 $target_a
	break
else
	echo -en "\e[1;31m target at $target_a is reachable, \e[0m"
	echo the search will continue ...
	tput sgr0
fi

done 

