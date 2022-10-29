#!/usr/bin/env python3

import time
import math

import sys
sys.path.append("./Servo_Driver_HAT")
import PCA9685

class ServoDriver:
  # Variables
  __LEFT_WHEEL           = 15       # port 3 = Left wheel
  __RIGHT_WHEEL          = 3        # port 15 = right wheel
  __WHEEL_DIAMETER       = 66.5     # diameter of wheel = 66.5 mm
  __MOVE_SPEED           = 24       # movement speed of the robot, in cm/second ori = 24
  __ANGULAR_SPEED        = 180      # angular speed of the robot, in degrees/second ori = 300
  __PULSE_OFFSET         = 44       # offset value of pulse, in micro-seconds

  def __init__(self):
    #setup servo by creating a PCA9685 instance
    self.servo = PCA9685.PCA9685(0x40, debug=False)
    self.servo.setPWMFreq(50)

  def stopServo(self, time_til_stop):
    #stop the servo in tts seconds, tts = 0 means the servo stops immediately
    time.sleep(time_til_stop)
    self.servo.setServoPulse(self.__LEFT_WHEEL,  0 )
    self.servo.setServoPulse(self.__RIGHT_WHEEL, 0 )
    time.sleep(1)

  def moveStraight(self, dist, backwards=False, pwr=0.2):
    if backwards == False:
      print("\n-- Left Wheel --")
      self.servo.setServoPulse(self.__LEFT_WHEEL,   1500-int(pwr*500) +self.__PULSE_OFFSET)
      print("-- Right Wheel --")
      self.servo.setServoPulse(self.__RIGHT_WHEEL,  1500+int(pwr*500) +self.__PULSE_OFFSET)
    else:  
      print("\n-- Left Wheel --")
      self.servo.setServoPulse(self.__LEFT_WHEEL,   1500+int(pwr*500) +self.__PULSE_OFFSET)
      print("-- Right Wheel --")
      self.servo.setServoPulse(self.__RIGHT_WHEEL,  1500-int(pwr*500) +self.__PULSE_OFFSET)
  
    #calculations of the travel time, tt
    tt = round(dist / self.__MOVE_SPEED, 2)
    print("[92m[m][0m Moving " + str(round(dist,1)) + " centimeters  in " + str(tt) + " seconds")
    
    #constant speed for tt seconds, until servo stops
    self.stopServo(tt)

  def rotateSelf(self, rot, clockwise=False, pwr=0.2):
    #perform clockwise/anticlockwise rotation
    if clockwise == False:
      print("\n-- Both wheels--")
      self.servo.setServoPulse(self.__LEFT_WHEEL, 1500-int(pwr*500) +self.__PULSE_OFFSET)
      self.servo.setServoPulse(self.__RIGHT_WHEEL,1500-int(pwr*500) +self.__PULSE_OFFSET)
    else: 
      print("\n-- Both wheels --")
      self.servo.setServoPulse(self.__LEFT_WHEEL, 1500+int(pwr*500) +self.__PULSE_OFFSET)
      self.servo.setServoPulse(self.__RIGHT_WHEEL,1500+int(pwr*500) +self.__PULSE_OFFSET)

    #calculation of rotation time, rt
    rt = round(rot / self.__ANGULAR_SPEED, 2)
    print("[93m[r][0m Rotating " + str(round(rot,1)) + " degrees  in " + str(rt) + " seconds")
    
    self.stopServo(rt)

  def testCode(self):
    self.rotateSelf(360, clockwise=False)
    #self.moveStraight(20)
    time.sleep(1)
    self.stopServo(0)



 


