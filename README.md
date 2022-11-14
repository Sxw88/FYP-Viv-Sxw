# FYP-Viv-Sxw

## Brief Description
In our capstone project (FYP), several swarm robots using Raspberry Pi controllers are programmed to demonstrate swarm behaviours.

## Installation:
Clone the project's GitHub repository to /home/pi, and then in the project's root folder, there is an initialisation script `init.sh`. Run the initialisation script once to setup the project. Sudo privileges are needed to run the initialisation script, alongside with a stable Internet connection in order to download the required packages.

### Potential issue with setting up Batman-adv
bat0 not showing up as a Batman-adv interface after reboot. 
This issue can be fixed by following this tutorial: https://github.com/binnes/WiFiMeshRaspberryPi/issues/8

## Enabling the I2C interface
In order for the servo driver to work, the i2c interface of the raspberry pi needs to be enabled. Use the command
`sudo raspi-config`
to enter the configuration menu and enable the i2c interface.

## Equipment / Specs
- Raspberry Pi 4b with 3D printed casing, bi-directional wheel-drive connected to PCA9685 servo drivers.
- Pi OS version: Raspbian GNU/Linux 10 (buster)
