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
##import ble_rssi as blescan

LOCAL_BLE_MAC = "AA:AA:AA:AA:AA:AA"
with open('mac.add', 'r') as f:
    LOCAL_BLE_MAC = f.readline()
    LOCAL_BLE_MAC = LOCAL_BLE_MAC[:-1]


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
    P0 = -44
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

def scanRSSI(timeout):
    """Scan RSSI of nearby BLE devices, and save info in JSON"""
    
    ##blescan.runscan(timeout) 
    # to avoid race condition, sleep for 1 second
    time.sleep(1)
    
    # read results of scan from JSON file format
    RSSI_LIST = []
    with open("ble/RSSI.json", 'r') as read_file:
        RSSI_LIST = json.load(read_file)

    # format each device in a new JSON list with distance conversion
    NEW_LIST = {}
    for device in RSSI_LIST:
        dist = rssi_to_distance(int(RSSI_LIST[device]["RSSI"]))
        
        time_passed = datetime.now() - datetime.strptime(RSSI_LIST[device]["last-seen"], "%Y-%m-%d,%H:%M:%S")
        if time_passed.total_seconds() < 100000: 
            NEW_LIST[makeKey(LOCAL_BLE_MAC, device)] = {"weight": dist, "timestamp": RSSI_LIST[device]["last-seen"]}

    # Write JSON data to file
    with open('GRAPH.json', 'w') as output_file:
        json.dump(NEW_LIST, output_file, indent=2)
        
    

if __name__ == "__main__":

    MAC1 = "53-02-16-1C-23-E5"
    MAC2 = "F5-B9-EB-C9-B9-8C"
    
    print(makeKey(MAC1, MAC2))
    print(makeKey(MAC2, MAC1))

    
    scanRSSI(20)

    
