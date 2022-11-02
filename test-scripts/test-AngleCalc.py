from datetime import datetime
import time
import math
import zlib
import json
import sys

def getAngletoRefNode(d1, d2, dm):
    """
    Returns angle theta given d1, d2, and dm such that
        d1 is the initial distance between current node and reference node
        d2 is the updated distance betweem current node and reference node
        dm is the distance moved by the current node 
    This function is used to calculate the angle for the robot to turn towards the reference node
    """
    var_x = (d2*d2 + dm*dm - d1*d1) / (2 * d2 * dm)
    print("d1 : " + str(d1))
    print("d2 : " + str(d2))
    print("dm : " + str(dm))
    
    try:
        theta = math.degrees(math.acos(var_x))
        theta = 180 - theta 
        return int(theta)
    except:
        print("Math error: try again.")
        return -1

print(getAngletoRefNode(133,91, 50))
# supposed to return 40.5 degrees (rounded to 40)
