#!/usr/bin/env python3

import math

def calc_dist_dir_tri(d0, d1, d2, debug=False):
    """calculate angle (in degrees) required for moving towards triangle position"""

    try:
        var_x = round((((d0 * d0) + (d1 * d1) - (d2 * d2))/(2 * d0 * d1)), 4)
        if debug:
            print("var x: " + str(var_x))
        theta1 = math.degrees(math.acos(var_x))
        if debug:
            print("theta1: " + str(theta1))

        var_y = math.cos(math.radians(60 - theta1))
        if debug:
            print("\nvar y: " + str(var_y))
        d = round(math.sqrt((d1 * d1) + (d0 * d0) - (2 * d1 * d0 * var_y)), 2)
        if debug:
            print("value of d: " + str(d))

        var_z = round((((d1 * d1) + (d * d) - (d0 * d0)) / (2 * d1 * d)), 4)
        if debug:
            print("\nvar z: " + str(var_z))
        theta2 = math.degrees(math.acos(var_z))
        if debug:
            print("theta2: " + str(theta2))

        theta = 180 - theta2 + theta1

        return [d, theta]
    except:
        print("\033[1;31mMath error\033[0m: try again.")
        return [0,0]

def calc_dir_align(d0, d1, d2, d3, d4, df, debug=False):
    """calculate angle (in degrees) required for alignment of robot's facing direction"""

    try:
        var_x = round((((df * df) + (d2 * d2) - (d4 * d4))/(2 * df * d2)), 4)
        if debug:
            print("var x: " + str(var_x))
        theta1 = math.degrees(math.acos(var_x))
        if debug:
            print("theta1: " + str(theta1))

        var_y = round((((d2 * d2) + (d0 * d0) - (d1 * d1))/(2 * d2 * d0)), 4)
        if debug:
            print("\nvar y: " + str(var_y))
        theta2 = math.degrees(math.acos(var_y))
        if debug:
            print("theta2: " + str(theta2))

        theta = theta1 - theta2
        return int(theta)
    except:
        print("\033[1;31mMath error\033[0m: try again.")
        return 1

if __name__ == "__main__":
    print("Helloworld testing")

    #print(calc_dist_dir_tri(50, 40, 30, debug=True))
    print(calc_dir_align(50, 30, 46, 40, 65, 50, debug=True))
