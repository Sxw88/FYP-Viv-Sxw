import time
import math

class SwarmRobot:
  # Variables
  LEFT_WHEEL           = 3      #port 3 = Left wheel
  RIGHT_WHEEL          = 15     #port 15 = right wheel
  WHEEL_DIAMETER       = 66.5   #diameter of wheel = 66.5 mm
  distance_travelled   = 0
  
  def __init__(self):
    #setup servo by creating a PCA9685 instance
    self.distance_travelled = 0

  def forwardCycle(self, c_range=1):
    # movement based on the sample code, 0 to 180 degrees
    # c_range=1 represents 180 degrees cycle, <1 represents a partial cycle
    if c_range == 0:
      c_range = 0.1     #minimum value of c_range
      
    cycle_limit = 500 + 2000*c_range
    for i in range(500, math.floor(cycle_limit), 10):
      self.distance_travelled += self.WHEEL_DIAMETER/400
      #time.sleep(0.02)

  def backwardCycle(self, c_range=1):
    # movement based on the sample code, 0 to 180 degrees
    # c_range=1 represents 180 degrees cycle, <1 represents a partial cycle
    if c_range == 0:
      c_range = 0.1     #minimum value of c_range
      
    cycle_limit = 500 + 2000*c_range
    for i in range(math.floor(cycle_limit), 500, -10):
      self.distance_travelled -= self.WHEEL_DIAMETER/4000
      #time.sleep(0.02)

  def moveForward(self, dist, backwards=False):
    #based on distance (in meters), calculate number of cycles needed
    cycles = round(((dist*1000) / self.WHEEL_DIAMETER), 1)
    #*2 to compensate for 180 degrees rotation instead of 360 degrees
    cycles = cycles*2
    print("cycles needed: " + str(cycles))
    
    if backwards == False:
      for i in range(int(cycles)):
        self.forwardCycle(1)
        print("cycle " + str(i) + " completed")
        self.printDist()
      self.forwardCycle(cycles - math.floor(cycles))
    else:
      for i in range(round(cycles*2)):
        self.backwardCycle(1)
        print("cycle " + str(i) + " completed")
        self.printDist()
      self.backwardCycle(cycles - math.floor(cycles))

  def printDist(self):
    print(str(round(self.distance_travelled, 2)) + " millimeters travelled")

if __name__=='__main__':
    #create new SwarmRobot instance
    srob = SwarmRobot()

    #this part is just to test out the movement
    #move forward, stop, move backwards
    srob.moveForward(0.7, backwards=False)

    srob.printDist()
