#!/usr/bin/env python3

# class to facilitate exchange of the collected RSSI information
# which is represented by a graph and stored in JSON format.
#
# CRC32 hash function is used to shorten the unique key 
# formed by the combination of MAC addresses of nodes.

from datetime import datetime
import time
import math
import zlib
import json
import sys
sys.path.append("./ble")
import ble_rssi as blescan
from ble_rssi import getJSONData

LOCAL_BLE_MAC = "BB:BB:BB:BB:BB:BB"

with open('info.add', 'r') as f:
    LOCAL_BLE_MAC = f.readline()
    LOCAL_BLE_MAC = f.readline()
    LOCAL_BLE_MAC = f.readline()
    LOCAL_BLE_MAC = LOCAL_BLE_MAC[:-1].upper()
    print(f"Local BLE/WLAN MAC Address: {LOCAL_BLE_MAC}")


def makeKey(node1, node2):

    # key is the representation of two nodes forming the edge
    key_MAC = ""
    if node1 < node2:
        key_MAC = node1 + "+" + node2
    else:
        key_MAC = node2 + "+" + node1
        
    encoded_key = key_MAC.encode()

    # hash the key_MAC variable to produce a shorter unique key
    key_edge = hex(zlib.crc32(encoded_key) & 0xffffffff)
    key_edge = key_edge[2:]

    return key_edge


def getDistance(P1_MAC, P2_MAC):
    """Gets the distance from GRAPH.json"""
    with open("GRAPH.json", "r") as f:
        G_LIST = json.load(f)

    rdist = int(float(getJSONData(G_LIST, makeKey(P1_MAC, P2_MAC), "weight"))*100)
    print("The estimated distance to the reference node is: \033[1;33m" + str(rdist) + " centimeters\033[0m")

    return rdist


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
        theta = int(math.degrees(math.acos(int(var_x))))
        theta = 180 - theta 
        return theta
    except:
        print("Math error: try again.")
        return -1


def factorial(num):  
    f = 1    
    if num < 0:    
       print(" Factorial does not exist for negative numbers")
       return 1
    elif num == 0:    
       print("The factorial of 0 is 1")
       return 1
    else:    
       for i in range(1,num + 1):    
           f = f*i
       return f 


def rssi_to_distance(rssi):
    """converts RSSI to distance (m), using Taylor series calculation"""
    d = 0
    
    # Measured variables, can be tweaked
    P0 = -59
    d0 = 1
    n = 2.5
    L = 6

    x = math.log(10, math.e) * ((P0-rssi)/(10*n))
    y = 1

    for i in range(1, L+1):
        y += pow(x, i) / factorial(i)

    d = d0 * y
    d = round(d, 2)
    
    return d

def scanRSSI(timeout, fast_mode=False):
    """Scan RSSI of nearby BLE devices, and save info in JSON"""
    
    blescan.runscan(timeout, -80, fast_mode=fast_mode) 
    # to avoid race condition, sleep for 1 second
    time.sleep(1)
    
    # read results of scan from JSON file format
    RSSI_LIST = []
    with open("ble/RSSI.json", 'r') as read_file:
        RSSI_LIST = json.load(read_file)

    # format each device in a new JSON list with distance conversion
    NEW_LIST = {}
    for device in RSSI_LIST:
        print("\n-------------Device-----------------")
        print(RSSI_LIST[device])
        print("------------------------------------\n")
        dist = rssi_to_distance(int(RSSI_LIST[device]["RSSI"]))
        
        time_passed = datetime.now() - datetime.strptime(RSSI_LIST[device]["Last-Seen"], "%Y-%m-%d,%H:%M:%S")
        if time_passed.total_seconds() < 3000: 
            
            node1 = LOCAL_BLE_MAC
            node2 = device
            if device < LOCAL_BLE_MAC:
                node1 = device
                node2 = LOCAL_BLE_MAC

            NEW_LIST[makeKey(LOCAL_BLE_MAC, device)] = { 
                    "MAC-1": node1,
                    "MAC-2": node2,
                    "weight": dist, 
                    "timestamp": RSSI_LIST[device]["Last-Seen"]
                    }

    # Write JSON data to file
    with open('GRAPH.json', 'w') as output_file:
        json.dump(NEW_LIST, output_file, indent=2)

        
def estDist(rep, timeout):
    """estimate distance to neighbouring nodes by scanning RSSI repeatedly and getting the average value"""

    for i in range(0, rep):
        # read distance (weight) from GRAPH.json
        GLIST1 = []
        with open("GRAPH.json", 'r') as read_file:
            GLIST1 = json.load(read_file)
        
        scanRSSI(timeout, fast_mode=True)
        
        # read distance (weight) from GRAPH.json again
        GLIST2 = []
        with open("GRAPH.json", 'r') as read_file:
            GLIST2 = json.load(read_file)

        for device in GLIST1:
            GLIST1[device]["weight"] = round((GLIST1[device]["weight"]*i + GLIST2[device]["weight"]) / (i+1), 2)

        # Write JSON data to file
        with open('GRAPH.json', 'w') as output_file:
            json.dump(GLIST1, output_file, indent=2)        



if __name__ == "__main__":

    MAC1 = "53-02-16-1C-23-E5"
    MAC2 = "F5-B9-EB-C9-B9-8C"
    
    print(makeKey(MAC1, MAC2))
    print(makeKey(MAC2, MAC1))
    
    scanRSSI(10, fast_mode=True)

    # Read MAC from device info.add
    with open("info.add") as f:
        MAC1 = f.readline()
        MAC1 = f.readline()
        MAC1 = f.readline()
        MAC1 = MAC1[:-1]

    print(MAC1)
    MAC2 = "DC:A6:32:D3:4F:11"
    
    G_LIST = []
    with open("GRAPH.json") as f:
        G_LIST = json.load(f)
        print(G_LIST)

    print(makeKey(MAC1, MAC2))
    print(getJSONData(G_LIST, makeKey(MAC1,MAC2), "weight"))


    
