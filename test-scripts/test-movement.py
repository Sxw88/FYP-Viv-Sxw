#!/usr/bin/python3

#import time
#import math
#import smbus

import sys
sys.path.append("/home/pi/FYP-Viv-Sxw")
import SwarmRobot

if __name__=='__main__':
    #create new SwarmRobot instance
    srob = SwarmRobot.SwarmRobot()

    #this part is just to test out the movement
    #move forward, stop, move backwards
    srob.testCode()
