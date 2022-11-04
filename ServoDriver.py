#!/usr/bin/env python3

import time
import math

import sys
sys.path.append("./Servo_Driver_HAT")
import PCA9685

class ServoDriver:
  # Variables
  __LEFT_WHEEL           = 15       # port 15 = Left wheel = West wheel
  __RIGHT_WHEEL          = 3        # port 3 = right wheel = East wheel
  __WHEEL_DIAMETER       = 66.5     # diameter of wheel = 66.5 mm
  __MOVE_SPEED           = 24       # movement speed of the robot, in cm/second ori = 24
  __ANGULAR_SPEED        = 360      # angular speed of the robot, in degrees/second ori = 300
  __PULSE_OFFSET         = 44        # offset value of pulse, in micro-seconds

  def __init__(self):
    # setup servo by creating a PCA9685 instance
    self.servo = PCA9685.PCA9685(0x40, debug=False)
    self.servo.setPWMFreq(50)

  def stopServo(self, time_til_stop):
    # stops the servo in tts seconds, tts = 0 means the servo stops immediately
    time.sleep(time_til_stop)
    self.servo.setServoPulse(self.__LEFT_WHEEL,  0 )
    self.servo.setServoPulse(self.__RIGHT_WHEEL, 0 )
    time.sleep(1)

  def moveStraight(self, dist, backwards=False, pwr=0.4):
    if backwards == True:
      print("\n-- Left Wheel --")
      self.servo.setServoPulse(self.__LEFT_WHEEL,   1500-int(pwr*800) +self.__PULSE_OFFSET)
      #self.servo.setServoPulse(self.__LEFT_WHEEL, 500)
      print("-- Right Wheel --")
      self.servo.setServoPulse(self.__RIGHT_WHEEL,  1500+int(pwr*800) +self.__PULSE_OFFSET)
      #self.servo.setServoPulse(self.__RIGHT_WHEEL, 2500)
    else:
      print("\n-- Left Wheel --")
      self.servo.setServoPulse(self.__LEFT_WHEEL,   1500+int(pwr*800) +self.__PULSE_OFFSET)
      #self.servo.setServoPulse(self.__LEFT_WHEEL, 2500)
      print("-- Right Wheel --")
      self.servo.setServoPulse(self.__RIGHT_WHEEL,  1500-int(pwr*800) +self.__PULSE_OFFSET)
      #self.servo.setServoPulse(self.__RIGHT_WHEEL, 500)

    # calculations of the travel time, tt
    tt = round(dist / self.__MOVE_SPEED, 2)
    print("[m] Moving " + str(round(dist,1)) + " centimeters  in " + str(tt) + " seconds")

    # constant speed for tt seconds, until servo stops
    self.stopServo(tt)

  def rotateSelf(self, rot, clockwise=False, pwr=0.2):
    # perform clockwise/anticlockwise rotation
    if clockwise == False:
      print("\n-- Both wheels--")
      #self.servo.setServoPulse(self.__LEFT_WHEEL, 1500-int(pwr*1000) +self.__PULSE_OFFSET)
      #self.servo.setServoPulse(self.__RIGHT_WHEEL,1500-int(pwr*1000) +self.__PULSE_OFFSET)
      self.servo.setServoPulse(self.__LEFT_WHEEL, 500)
      self.servo.setServoPulse(self.__RIGHT_WHEEL, 500)
    else:
      print("\n-- Both wheels --")
      #self.servo.setServoPulse(self.__LEFT_WHEEL, 1500+int(pwr*1000) +self.__PULSE_OFFSET)
      #self.servo.setServoPulse(self.__RIGHT_WHEEL,1500+int(pwr*1000) +self.__PULSE_OFFSET)
      self.servo.setServoPulse(self.__LEFT_WHEEL, 2500)
      self.servo.setServoPulse(self.__RIGHT_WHEEL, 2500)


    #calculation of rotation time, rt
    rt = round(rot / self.__ANGULAR_SPEED, 2)
    print("[r] Rotating " + str(round(rot,1)) + " degrees  in " + str(rt) + " seconds")

    self.stopServo(rt)


  def rotateSelf90(self, rot, clockwise=False):
    # performs clockwise / counterclockwise rotation in 90 degrees 
    r = rot

    print("Total rotation to be carried out: " + str(r) + " degrees" )

    while True:
      if r > 90:
        self.rotateSelf(90, clockwise=clockwise)
        r = r - 90
      else:
        self.rotateSelf(r, clockwise=clockwise)
        break


  def testCode(self):
    self.rotateSelf90(35, clockwise=False)
    #self.rotateSelf(180, clockwise=False)
    #self.rotateSelf(360, clockwise=True)
    #self.rotateSelf(180, clockwise=True)
    #self.moveStraight(100, backwards=True)
    #self.moveStraight(50, backwards=False)
    #self.moveStraight(50, backwards=True)
    #time.sleep(1)
    #self.stopServo(0)
