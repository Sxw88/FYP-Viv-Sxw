#!/bin/bash

#initialisation script, run this after cloning the GitHub repo

#setting up aliases
sudo echo '#adding custom aliases' >> /home/pi/.bashrc
sudo echo 'alias fyp="cd /home/pi/FYP-Viv-Sxw"' >> /home/pi/.bashrc
sudo echo 'alias test="./test.sh"' >> /home/pi/.bashrc
sudo echo 'alias stop="/home/pi/test-scripts/stop.py"' >> /home/pi/.bashrc

source /home/pi/.bashrc
