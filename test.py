#!/usr/bin/python

#import time
#import math
#import smbus

import sys
sys.path.append("./")
import SwarmRobot

if __name__=='__main__':
    #create new SwarmRobot instance
    srob = SwarmRobot()

    #this part is just to test out the movement
    #move forward, stop, move backwards
    srob.moveForward(0.5)
    srob.moveBackward(0.5)
