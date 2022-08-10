#!/usr/bin/python

import time
import math

import sys
sys.path.append("./Servo_Driver_HAT")
import PCA9685

class SwarmRobot:
  # Variables
  LEFT_WHEEL           = 15     #port 3 = Left wheel
  RIGHT_WHEEL          = 3      #port 15 = right wheel
  WHEEL_DIAMETER       = 66.5   #diameter of wheel = 66.5 mm

  def __init__(self):
    #setup servo by creating a PCA9685 instance
    self.servo = PCA9685.PCA9685(0x40, debug=False)
    self.servo.setPWMFreq(50)

  def stopServo(self, time_til_stop):
    #stop the servo in tts seconds, tts = 0 means the servo stops immediately
    time.sleep(time_til_stop)
    self.servo.setServoPulse(self.LEFT_WHEEL, 0)
    self.servo.setServoPulse(self.RIGHT_WHEEL, 0)

  def forwardCycle(self, c_range=1):
    # movement based on the sample code, 0 to 180 degrees
    # c_range=1 represents 180 degrees cycle, <1 represents a partial cycle
    if c_range == 0:
      c_range = 0.1     #minimum value of c_range
      
    cycle_limit = 500 + 2000*c_range
    for i in range(500, cycle_limit, 10):
      self.servo.setServoPulse(self.LEFT_WHEEL, i)
      self.servo.setServoPulse(self.RIGHT_WHEEL, i)
      time.sleep(0.02)

  def backwardCycle(self, c_range=1):
    # movement based on the sample code, 0 to 180 degrees
    # c_range=1 represents 180 degrees cycle, <1 represents a partial cycle
    if c_range == 0:
      c_range = 0.1     #minimum value of c_range
      
    cycle_limit = 500 + 2000*c_range
    for i in range(cycle_limit, 500, -10):
      self.servo.setServoPulse(self.LEFT_WHEEL, i)
      self.servo.setServoPulse(self.RIGHT_WHEEL, i)
      time.sleep(0.02)

  def moveForward(self, dist, backwards=False):
    #based on distance (in meters), calculate number of cycles needed
    cycles = round(((dist*1000) / self.WHEEL_DIAMETER), 1) #*1000 converts distance from meters to millimeters
    #*2 to compensate for 180 degrees rotation instead of 360 degrees
    cycles = cycles*2
   
    if backwards == False:
      for i in range(int(cycles)): 
        self.forwardCycle(1)
      self.forwardCycle(cycles - math.floor(cycles))
    else:
      for i in range(int(cycles)): 
        self.backwardCycle(1)
      self.backwardCycle(cycles - math.floor(cycles))

  def tryMoveForward(self):
    self.servo.setServoPulse(self.RIGHT_WHEEL, 1495)
    self.servo.setServoPulse(self.LEFT_WHEEL, 1612)
    
    #constanst speed
    time.sleep(3)
    self.stopServo(0)
    time.sleep(1)

    self.servo.setServoPulse(self.LEFT_WHEEL, 1495)
    self.servo.setServoPulse(self.RIGHT_WHEEL, 1612)
    
    #constanst speed
    time.sleep(3)
    self.stopServo(0)

  
  def nothing(self):
    for i in range(50, 300, 10):
      self.servo.setServoPulse(self.LEFT_WHEEL, 1550-i)
      self.servo.setServoPulse(self.RIGHT_WHEEL, 1550+i)
      time.sleep(0.01)
    
    #constanst speed
    time.sleep(2)
    self.stopServo(0)

    for i in range(300, 100, -20):
      self.servo.setServoPulse(self.LEFT_WHEEL, 1550-i)
      self.servo.setServoPulse(self.RIGHT_WHEEL, 1550+i)
      time.sleep(0.01)
    
    #pause here
    self.stopServo(1)
    time.sleep(1)

    for i in range(50, 300, 10):
      self.servo.setServoPulse(self.RIGHT_WHEEL, 1550-i)
      self.servo.setServoPulse(self.LEFT_WHEEL, 1550+i)
      time.sleep(0.01)

    #constant speed
    time.sleep(0.5)

    for i in range(300, 100, -20):
      self.servo.setServoPulse(self.RIGHT_WHEEL, 1550-i)
      self.servo.setServoPulse(self.LEFT_WHEEL, 1550+i)
      time.sleep(0.01)
    self.stopServo(1)
    time.sleep(1)


