#!/usr/bin/python3

import time
import math
import smbus

import sys
sys.path.append("/home/pi/FYP-Viv-Sxw/Servo_Driver_HAT")
import PCA9685

if __name__=='__main__':

  pwm = PCA9685.PCA9685(0x40, debug=False)
  pwm.setPWMFreq(50)
  while True:
   # setServoPulse(2,2500)
    for i in range(500,2500,10):
      pwm.setServoPulse(3,i)
      time.sleep(0.02)

    for i in range(2500,500,-10):
      pwm.setServoPulse(3,i)
      time.sleep(0.02)


