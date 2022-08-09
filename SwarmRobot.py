#!/usr/bin/python

import time
import math

import sys
sys.path.append("./Servo_Driver_HAT")
import PCA9685

class SwarmRobot:
  # Variables
  LEFT_WHEEL           = 3      #port 3 = Left wheel
  RIGHT_WHEEL          = 15     #port 15 = right wheel

  def __init__(self):
    #setup servo by creating a PCA9685 instance
    self.servo = PCA9685.PCA9685(0x40, debug=True)
    self.servo.setPWMFreq(50)

  def stopServo(self, time_til_stop):
    #stop the servo in tts seconds, tts = 0 means the servo stops immediately
    time.sleep(time_til_stop)
    self.servo.setServoPulse(LEFT_WHEEL, 0)
    self.servo.serServoPulse(RIGHT_WHEEL, 0)

  def moveForward(self, dist):
    #move forward <dist> meters
    #for now just some simple test code, need to find the speed of the robot first
    self.servo.setServoPulse(LEFT_WHEEL, 100)
    self.servo.serServoPulse(RIGHT_WHEEL, 100)

    #the robot runs for 1 second, then stops. The 1 second is just a placeholder.
    #We need to find the speed, then tts can be expressed as dist/speed
    time_til_stop = 1 
    self.stopServo(time_til_stop)

  def moveBackward(self, dist):
    #move backwards <dist> meters
    #assumption of backwards movement is that the pulse is set to negative,
    #gonna need to test that tho
    self.servo.setServoPulse(LEFT_WHEEL, -100)
    self.servo.serServoPulse(RIGHT_WHEEL, -100)

    time_til_stop = 1 
    self.stopServo(time_til_stop)
