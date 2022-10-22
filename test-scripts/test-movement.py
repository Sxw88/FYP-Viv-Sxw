#!/usr/bin/env python3

#import time
#import math
#import smbus

import sys
sys.path.append("/home/pi/FYP-Viv-Sxw")
from ServoDriver import ServoDriver

if __name__=='__main__':
    #create new SwarmRobot instance
    srv = ServoDriver()

    #this part is just to test out the movement
    #move forward, stop, move backwards
    srv.testCode()
