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
  MOVE_SPEED           = 10     #movement speed of the robot, in centimeters/second
  ANGULAR_SPEED        = 90     #angular speed of the robot, in degrees/second

  def __init__(self):
    #setup servo by creating a PCA9685 instance
    self.servo = PCA9685.PCA9685(0x40, debug=False)
    self.servo.setPWMFreq(50)

  def stopServo(self, time_til_stop):
    #stop the servo in tts seconds, tts = 0 means the servo stops immediately
    time.sleep(time_til_stop)
    self.servo.setServoPulse(self.LEFT_WHEEL, 0)
    self.servo.setServoPulse(self.RIGHT_WHEEL, 0)
    time.sleep(1)

  def moveForward(self, dist, backwards=False):
    if backwards == False:
      self.servo.setServoPulse(self.LEFT_WHEEL, 2500)
      self.servo.setServoPulse(self.RIGHT_WHEEL, 500)
    else:  
      self.servo.setServoPulse(self.LEFT_WHEEL, 500)
      self.servo.setServoPulse(self.RIGHT_WHEEL, 2500)
      
    #calculations of the travel time, tt
    tt = round(dist / MOVE_SPEED, 1)
    print("[92m[m][0m Moving " + round(dist,1) + " meters  in " + tt + " seconds")
    
    #constant speed for tt seconds, until servo stops
    self.stopServo(tt)

  def rotateSelf(self, rot, clockwise=False):
    #perform clockwise/anticlockwise rotation
    if clockwise == False:
      self.servo.setServoPulse(self.LEFT_WHEEL, 500)
      self.servo.setServoPulse(self.RIGHT_WHEEL, 500)
    else: 
      self.servo.setServoPulse(self.LEFT_WHEEL, 2500)
      self.servo.setServoPulse(self.RIGHT_WHEEL, 2500)
      
    #calculation of rotation time, rt
    rt = round(rot / ANGULAR_SPEED, 1)
    print("[93m[m][0m Rotating " + round(rot,1) + " degrees  in " + rt + " seconds")
    
    self.stopServo(rt)

  def tryMoveForward(self):
    moveForward(20, False)

 


