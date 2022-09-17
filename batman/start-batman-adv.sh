#!/bin/bash
#batman-adv interface to use
sudo batctl if add wlan0
sudo ifconfig bat0 mtu 1468

#Tell batman-adv this is a gateway client
sudo batctl gw_mode client

#Activates batman-adv interfaces
sudo ifconfig wlan0 up
sudo ifconfig bat0 up

sleep 10
sudo /home/pi/FYP-Viv-Sxw/batman/get-IP.sh > /home/pi/FYP-Viv-Sxw/batman/get-IP.log
