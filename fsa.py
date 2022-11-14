#!/usr/bin/env python3

from __future__ import annotations

import time
import json
import sys
import random

from abc import ABC, abstractmethod
from GraphEx import (
        scanRSSI, 
        compareKnownPeers,
        makeKey, 
        getDistance, 
        rssi_to_distance,
        estDist,
        calc_dir_align,
        calc_dist_dir_tri,
        getAngletoRefNode, 
        LOCAL_BLE_MAC
        )
from ServoDriver import ServoDriver

sys.path.append("./ble")
from ble_rssi import getJSONData

sys.path.append("./batman")
from WxAdHocComm import WxAdHocComm

next_step   = "non"
adist       = 50        # How many centimeters apart between the swarm robots at anchored state
srv         = None      # Servo Driver Object
REF1        = None      # Reference Node 1
REF2        = None      # Reference Node 2
unique_ID   = "20"

# The Finite State Automata (FSA) class is the context. It should be initiated with a default state.
class FSA:

    _state = None

    def __init__(self, state: State) -> None:
        self.setFSA(state)

    # method to change the state of the object
    def setFSA(self, state: State):

        self._state = state
        self._state.fsa = self

    def presentState(self):
        print(f"[ Currently in State: {type(self._state).__name__} ]")

    # the methods for executing the Finite State Machine's functionality.
    # These depends on the current state of the object.
    def startInitAnchoring(self):
        self._state.startInitAnchoring()

    def startLocalization(self):
        self._state.startLocalization()

    def startTTE(self): # Travel-to-Edge state
        self._state.startTTE()

    def startTriangulation(self):
        self._state.startTriangulation()

    def startAnchored(self):
        self._state.startAnchored()



# The common state interface for all the states
class State(ABC):
    @property
    def fsa(self) -> FSA:
        return self._fsa

    @fsa.setter
    def fsa(self, fsa: FSA) -> None:
        self._fsa = fsa

    @abstractmethod
    def startInitAnchoring(self) -> None:
        pass

    @abstractmethod
    def startLocalization(self) -> None:
        pass

    @abstractmethod
    def startTTE(self) -> None:
        pass

    @abstractmethod
    def startTriangulation(self) -> None:
        pass

    @abstractmethod
    def startAnchored(self) -> None:
        pass


# The concrete states
# Six total states: Initialisation, Init-Anchoring, Localization,
# Travel-to-Edge (TTE), Triangulation, and Anchored

class Initialisation(State):

    def __init__(self):
        """The code for the Initialisation state goes here"""
        
        print("\033[1;32m[*]\033[0m Currently in the Initialisation State")
        global next_step
        next_step = "ini"

        # Update current state in the 'state' file
        with open("state", "w") as f_write:
            f_write.write(next_step+"\n")

        # Reset list of known peers in the 'known_peers' file
        with open("known_peers", "w") as f_write:
            f_write.write("[]")
        
        # Initialize the Servo Driver object
        global srv
        srv = ServoDriver()
        srv.testCode() # rotate 360 degrees
        
        global unique_ID
        # getting the unique ID from info.add file
        with open("info.add") as f_read:
            line_to_read = f_read.readline()
            line_to_read = f_read.readline()
            unique_ID = line_to_read[10:-1]

        global REF1
        
        while next_step == "ini":
            """ Initialisation loop, will only break under 2 conditions:
                    1) Robot selected for Init-Anchoring process
                    2) More than 2 anchors, proceed to Localize & Triangulate
            """
            ini_list = [] # list of robots currently in the initialisation process 
            anc_count = 0 # total number of peers in init-anchoring / anchored states   
            
            # Scan and check for peers which are online
            scanRSSI(50)
            missing_peers = str(compareKnownPeers())
            if missing_peers != "[]":
                print("\033[1;33mWarning:\033[0m These peers have not been scanned: " + missing_peers)

            # Check for any anchored peers from RSSI.json file
            with open("./ble/RSSI.json", "r") as f_rssi:
                
                print("Checking for peers in Init-Anchoring / Anchored states:")
                rssi_list = json.load(f_rssi)
                
                for device in rssi_list:
                    device_state = getJSONData(rssi_list, device, "State")
                    #print("Device MAC: " + str(device) + "\nDevice State: " + str(device_state) + "\n")

                    if device_state == "anc" or device_state == "i-a" or device_state == "i2a":
                        # Copy the anchored device JSON object to a new list
                        anc_count = anc_count +1
                        if device_state == "anc":
                            REF1 = device                   # to be used as reference node in i2a state 
                    elif device_state == "ini":
                        # add unique ID to the list
                        device_uID = getJSONData(rssi_list, device, "Name")
                        ini_list.append(device_uID[7:])
                        
            print("Number of Anchored/Anchoring devices detected: " + str(anc_count))
            
            if anc_count >= 2:      # End Initialisation state and enter Localization state
                next_step = "lcl"
            elif anc_count == 1:    # Else, Proceed with Init-Anchoring process
                next_step = "i2a"
                print("\tReference node: " + REF1)
            elif anc_count == 0:
                next_step = "i-a"
                
            # If it does not have the smallest ID,
            # the robot will stay in the initialisation loop
            for device_uID in ini_list:
                print("Comparing ID: Pi-BLE-" + unique_ID + " with ID: Pi-BLE-" + device_uID, end=" ... ")

                if (int(device_uID) < int(unique_ID)):
                    print(device_uID + " is smaller. ")
                    next_step = "ini"
                    print("The script will sleep for 5 seconds and try again.")
                    time.sleep(5)
                    break
                else:
                    print(unique_ID + " is smaller")
           
    # The robot starts to anchor itself if no other reference points can be found
    def startInitAnchoring(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Initialisation-Anchoring state...")
        print("\n-------------------------------------------------------------------------------\n")
        self.fsa.setFSA(InitAnchoring())

    # The robot enters Localization state if >2 reference points are found
    def startLocalization(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Localization state...")
        print("\n-------------------------------------------------------------------------------\n")
        self.fsa.setFSA(Localization())

    # Irrelevant states
    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTriangulation(self) -> None:
        print("WARNING: No actions will be carried out")

    def startAnchored(self) -> None:
        print("WARNING: No actions will be carried out")



class InitAnchoring(State):
    def __init__(self):
        """Code for the Initialisation-Anchoring state goes here """
        
        print("\033[1;32m[*]\033[0m Currently in the Initialisation-Anchoring State")
        global next_step
        
        if next_step == "i-a":
            # First to anchor
            next_step = "anc"
            
        elif next_step == "i2a":
            # Need to check the distance between this robot and first anchored robot
            
            mdist  = 50 # Initialize moving distance to 50 (centimeters)
            rdist1 = 0  # Read the distance to the anchor node (stored in GRAPH.json)
            rdist2 = 0

            # The first scan should take a longer time for better accuracy
            estDist(15, 10, target_MAC=REF1.upper()) # scan 15 times for 3 seconds
            rdist1 = getDistance(LOCAL_BLE_MAC, REF1)
            
            # Move a fixed distance (mdist)
            srv.moveStraight(mdist)
            
            # And then determine new distance to the reference node (rdist2)
            rdist2 = rdist1 + mdist + 10        # rdist2 should always be smaller
            while rdist2 > (rdist1 + mdist) or rdist2 < (rdist1 - mdist):    # than the sum of rdist and mdist
                estDist(7, 10, target_MAC=REF1.upper()) # scan 7 times for 3 seconds
                rdist2 = getDistance(LOCAL_BLE_MAC, REF1) 

            # Attempt clockwise rotation first
            rot = -1
            while rot == -1:
                rot = getAngletoRefNode(rdist1, rdist2, mdist)

                if rot == -1:  # repeat scanning and moving process again
                    print("\033[1;31m[*] Math Error: \033[0m Will proceed to scan again")
                    estDist(7, 3, target_MAC=REF1.upper()) # scan 7 times for 3 seconds
                    rdist1 = getDistance(LOCAL_BLE_MAC, REF1)

                    # Move a fixed distance (mdist)
                    srv.moveStraight(mdist)
                    
                    # And then determine new distance to the reference node (rdist2)
                    rdist2 = rdist1 + mdist + 10        # rdist2 should always be smaller
                    while rdist2 > (rdist1 + mdist) or rdist2 < (rdist1 - mdist):    # than the sum of rdist and mdist
                        estDist(7, 10, target_MAC=REF1.upper()) # scan 7 times for 3 seconds
                        rdist2 = getDistance(LOCAL_BLE_MAC, REF1)

            srv.rotateSelf90(rot, clockwise=True)

            # Move forward/backwards x meters to move to desired distance
            mdist = rdist2 - adist
            if mdist < 0:
                srv.moveStraight(0-mdist, backwards=True)
            else:    
                srv.moveStraight(mdist)

            # Scan and Check the new distance
            estDist(7, 10, target_MAC=REF1.upper()) # scan 7 times for 3 seconds
            rdist1 =  getDistance(LOCAL_BLE_MAC, REF1)
            
            if rdist1 < adist + 10 and rdist1 > adist -10:
                # if distance is acceptable within margin error 10 cm
                print("Estimated distance to reference node: " + str(rdist1) + " centimeters. ")
                print("\033[32mProceeding to Anchored state\033[0m")
            else:
                # reverse to previous position and repeat in another direction
                print("Estimated distance to reference node: " + str(rdist1) + " centimeters. ")
                print("\033[1;34mRepeating anchoring process ...\033[0m")
                
                if mdist < 0:
                    srv.moveStraight(0-mdist, backwards=False)
                else: 
                    srv.moveStraight(mdist, backwards=True)

                # Attempt rotation in anticlockwise direction
                rot = rot*2
                srv.rotateSelf90(rot, clockwise=False)

                # Move forward/backwards x meters to move to desired distance
                mdist = rdist2 - adist
                if mdist < 0:
                    srv.moveStraight(0-mdist, backwards=True)
                else:    
                    srv.moveStraight(mdist)

                # Scan and Check the new distance
                estDist(7, 10, target_MAC=REF1.upper()) # scan 7 times for 3 seconds
                rdist1 =  getDistance(LOCAL_BLE_MAC, REF1)
                
            next_step = "anc"


    # Proceeds to Anchored state 
    def startAnchored(self) -> None: 
        print("\033[1;33m[*]\033[0m Switching to the Anchored state...")
        print("\n-------------------------------------------------------------------------------\n")
        self.fsa.setFSA(Anchored())
    
    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startLocalization(self) -> None:
        print("WARNING: No actions will be carried out")
    
    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTriangulation(self) -> None:
        print("WARNING: No actions will be carried out")



class Localization(State):
    """ This state is similar to initialisation, robots will loop in this step while waiting for
        for other robots to complete the TTE/ Triangulation state
    """ 
    
    def __init__(self):
        print("\033[1;32m[*]\033[0m Currently in the Localization state")
        # main code for Localization goes here
        #Pseudocode : loop (check for peers in TTE/Tri states - wait some time) - wait for your turn - decide TTE/Tri state 
        
        global next_step
        global unique_ID
        
        while next_step == "lcl":
            
            # Scan for peers currently in TTE/ Triangulation state
            scanRSSI(50)
            
            tri_count = 0
            anc_count = 0           # This is used later to determine whether or not to proceed with Triangulation (SPECIAL CASE)
            lcl_list = []           # list of robots currently in the localisation process 
            anc_list = []           # list containing RSSI information to anchored robots
            
            print("\033[1;32mScanning Complete.\033[0m Now checking for peers in TTE / Triangulation state:")
            # Check for peers in TTE / Triangulation state from RSSI.json file
            with open("./ble/RSSI.json", "r") as f_rssi:
                rssi_list = json.load(f_rssi)
                
                for device in rssi_list:
                    device_state = getJSONData(rssi_list, device, "State")
                    #print("Device MAC: " + str(device) + "\nDevice State: " + str(device_state) + "\n")

                    if device_state == "tte" or device_state == "tri":
                        tri_count = tri_count + 1       # increment tri_count variable
                        print("\tNew device in TTE/Tri state detected, MAC address: " + device)
                    elif device_state == "lcl":
                        # add unique ID to the list
                        device_uID = getJSONData(rssi_list, device, "Name")
                        lcl_list.append(device_uID[7:])
                    elif device_state == "anc":
                        anc_count = anc_count + 1       # increment tri_count variable
                    
            if tri_count == 0:
                
                # decide whether to proceed with TTE or Triangulation
                                        # if > 2 nodes anchored
                if anc_count > 2:       # estimate distance - get distance to nearest 3 nodes
                    estDist(10, 10)     # if any one node > int(adist*1.2) cm, goto "tri"                
                                        # else goto "tte"
                    with open("./ble/RSSI.json", "r") as f_rssi:
                        rssi_list = json.load(f_rssi)
                        
                        for device in rssi_list:
                            device_state = getJSONData(rssi_list, device, "State")
                            
                            if device_state == "anc":
                                anc_list.append([device, getJSONData(rssi_list, device, "RSSI")])
                    
                    anc_list = sorted(anc_list)     # sort the list, 
                    try:
                        anc_list = anc_list[-3:]         # then take the last 3 elements (nearest 3 anchored nodes)
                    except:
                        print("\033[1;31mError: \033[0mItems not found in ANC_LIST")
                    
                    next_step = "tte"                       # go to tte state unless if any one node > adist cm + 20%, then goto "tri"
                    for rssi in anc_list:                                              
                        if int(rssi_to_distance(rssi) * 100) > int(adist*1.2):
                            next_step = "tri"
                            break
                
                elif anc_count == 2:    # SPECIAL CASE to proceed with Triangulation if exactly 2 anchors are found
                    next_step = "tri"
                    
                # another check to compare unique ID among localising peers
                # If it does not have the smallest ID,
                # the robot will stay in the initialisation loop
                for device_uID in lcl_list:
                    print("Comparing ID: Pi-BLE-" + unique_ID + " with ID: Pi-BLE-" + device_uID, end=" ... ")

                    if (int(device_uID) < int(unique_ID)):
                        print(device_uID + " is smaller. ")
                        next_step = "lcl"
                        break
                    else:
                        print(unique_ID + " is smaller")
                    
            if next_step == "lcl":
                rand_sleep = random.randint(8, 18)
                print("Detected " + str(tri_count) + " peers currently in TTE / Triangulation state. ")
                print("Detected " + str(anc_count) + " peers currently Anchored. ")
                print("\033[1;33m[*]\033[0m Script will sleep for " + str(rand_sleep) + " seconds and try again.")
                time.sleep(rand_sleep)
    
    # Enters Triangulation state if no TTE needed
    def startTriangulation(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Triangulation state...")
       	print("\n-------------------------------------------------------------------------------\n") 
        self.fsa.setFSA(Triangulation())
    
    # Travel-to-Edge if needed
    def startTTE(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Travel-to-Edge state...")
        print("\n-------------------------------------------------------------------------------\n")
        self.fsa.setFSA(TTE())

    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startLocalization(self) -> None:
        print("WARNING: No actions will be carried out")

    def startAnchored(self) -> None:
        print("WARNING: No actions will be carried out")



# pseudocode for triangulation process: 
class TTE(State):

    def __init__(self):
        print("\033[1;32m[*]\033[0m Currently in the Travel-to-Edge (TTE) state")
        # Main code for Travelling-to-Edge process goes here
        global next_step
        next_step = "tri" 

    # Enters Localization state if TTE is NOT successful
    def startLocalization(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Localization state...")
        print("\n-------------------------------------------------------------------------------\n")
        self.fsa.setFSA(Localization())

    # Enters Triangulation state if TTE successful
    def startTriangulation(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Triangulation state...")
        print("\n-------------------------------------------------------------------------------\n")
        self.fsa.setFSA(Triangulation())

    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startAnchored(self) -> None:
        print("WARNING: No actions will be carried out")
    


class Triangulation(State):

    def __init__(self):
        print("\033[1;32m[*]\033[0m Currently in the Triangulation state")
        # Main code for Triangulation process goes here
        
        global next_step
        next_step = "anc"
            
	# Scan RSSI of peers
        estDist(10, 10)
        # get closest anchored peers (REF1 and REF2)
        rssi_list = []
        with open("./ble/RSSI.json") as f_read:
            rssi_list = json.load(f_read)
        
        # get REF1 and d1
        global REF1
        REF1 = None
        d1 = 10000      # initialise distance d1 to 100 meters for comparison
        # get REF2 and d2
        global REF2
        REF2 = None
        d2 = 10000      # initialise distance d2 to 100 meters for comparison
        
        #for device in rssi_list:
        for device in rssi_list:
            #dist = int(rssi_to_distance(getJSONData(rssi_list, device, "RSSI"))*100)
            dist = getDistance(device, LOCAL_BLE_MAC)
            print("Device: " + device + ", distance: " + str(dist) + ", State: " + str(getJSONData(rssi_list,device,"State")) + ", RSSI: " + str(getJSONData(rssi_list, device, "RSSI")))
            # store distance in variable d1 and d2
            if getJSONData(rssi_list, device, "State") == "anc":
                if dist <= d1:
                    REF2 = REF1
                    REF1 = device
                    d2 = d1
                    d1 = dist 
                    print("Reference node 1: " + device)
                elif dist <= d2: 
                    REF2 = device
                    d2 = dist
                    print("Reference node 2: " + device)

		
	# Move fixed distance df
        df = 50
        srv.moveStraight(df)

	# Scan RSSI of peers again, get updated distance to REF1 and REF2
        estDist(10, 10)
        with open("./ble/RSSI.json") as f_read:
            rssi_list = json.load(f_read)
        
        global adist
        d3 = 0
        d4 = 0

        # store distance in variables d3 and d4
        for device in rssi_list:
            if device == REF1:
                #d3 = int(rssi_to_distance(getJSONData(rssi_list, device, "RSSI"))*100)
                d3 = getDistance(LOCAL_BLE_MAC, device)
            elif device == REF2:
                #d4 = int(rssi_to_distance(getJSONData(rssi_list, device, "RSSI"))*100)
                d4 = getDistance(LOCAL_BLE_MAC, device)

	# Compute rotational angle using known information, d1, d2, d3, d4, df 
        print("d0: " + str(adist) + ", d1: " + str(d1) + ", d2: " + str(d2) + ", d3: " + str(d3) + ", d4: " + str(d4))
        rot_degrees = calc_dir_align(adist, d1, d2, d3, d4, df)
	# and then carry out the rotation
        srv.rotateSelf90(rot_degrees, clockwise=True)

	# Move fixed distance df and compare updated distance
        srv.moveStraight(df)
        estDist(10, 10)
        with open("./ble/RSSI.json") as f_read:
            rssi_list = json.load(f_read)
            print("Read from RSSI.json: " + str(rssi_list))
        
        d5 = 0
        d6 = 0
        
        for device in rssi_list:
            if device == REF1:
                #d5 = int(rssi_to_distance(getJSONData(rssi_list, device, "RSSI"))*100)
                d5 = getDistance(LOCAL_BLE_MAC, device)
            elif device == REF2:
                #d6 = int(rssi_to_distance(getJSONData(rssi_list, device, "RSSI"))*100)
                d6 = getDistance(LOCAL_BLE_MAC, device)
                        
	# if moved further from REF2
        if d6 > d4:
	    # rotate 180
            srv.rotateSelf90(180)

        # Compute distance to travel and rotation angle
        print("d0: " + str(adist) + ", d1: " + str(d5) + ", d2: " + str(d6))
        list_dist_rot = calc_dist_dir_tri(adist, d5, d6)

        # move to position
        srv.rotateSelf90(list_dist_rot[1])
        srv.moveStraight(list_dist_rot[0])


    # Enters Localization state if Triangulation is NOT successful
    def startLocalization(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Localization state...")
        print("\n-------------------------------------------------------------------------------\n")
        self.fsa.setFSA(Localization())

    # Proceeds to Anchored stateif Triangulation is successful
    def startAnchored(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Anchored state...")
        print("\n-------------------------------------------------------------------------------\n")
        self.fsa.setFSA(Anchored())
    
    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTriangulation(self) -> None:
        print("WARNING: No actions will be carried out")
        


class Anchored(State):

    def __init__(self):
        print("\033[1;32m[*]\033[0m Successfully entered the Anchored state")
        # Code for Anchored state
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        time.sleep(3)

    def startAnchored(self) -> None:
        print("\033[1;33m[*]\033[0m Robot currently Anchored")
        time.sleep(3)

    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTTE(self) -> None:
        print("WARNING: No actions will be carried out")

    def startTriangulation(self) -> None:
        print("WARNING: No actions will be carried out")

    def startLocalization(self) -> None:
        print("WARNING: No actions will be carried out")



def startFSA():
    global next_step

    # Initialise robot object
    myRobot = FSA(Initialisation())
    #myRobot.presentState()
    
    # Infinite loop
    while 1 == 1:
        
        # Update current state in the 'state' file
        with open("state", "w") as f_write:
            f_write.write(next_step + "\n")

        # Switch into the corresponding states
        if next_step == "i-a" or next_step == "i2a":
            myRobot.startInitAnchoring()
        elif next_step == "lcl":
            myRobot.startLocalization()
        elif next_step == "tte":
            myRobot.startTTE()
        elif next_step == "tri":
            myRobot.startTriangulation()
        elif next_step == "anc":
            myRobot.startAnchored()


if __name__ == "__main__":
    # The client code.

    startFSA()



"""


                   ┌───────────────────┐
                   │                   │
                   │                   │
                   │ Initial-Anchoring ├──────────────────────────────────────────────┐
                   │                   │                                              │
                   │                   │                                              │
                   └─────────▲─────────┘                                              │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                   ┌─────────┴─────────┐                                    ┌─────────▼─────────┐
                   │                   │                                    │                   │
                   │                   │                                    │                   │
    ──────────────►│  Initialisation   │                                    │      Anchored     │
                   │                   │                                    │                   │
                   │                   │                                    │                   │
                   └─────────┬─────────┘                                    └─────────▲─────────┘
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                             │                                                        │
                   ┌─────────▼─────────┐                               ┌──────────────┴─────┐
                   │                   │                               │                    │
                   │                   │                               │                    │
                   │   Localization    ◄───────────────────────────────►    Triangulation   │
                   │                   │                               │                    │
                   │                   │                               │                    │
                   └─────────▲─────────┘                               └──────────▲─────────┘
                             │                                                    │
                             │                                                    │
                             │                                                    │
                             │               ┌────────────────────────┐           │
                             │               │                        │           │
                             │               │                        │           │
                             └───────────────►     Travel-to-Edge     ├───────────┘
                                             │                        │
                                             │                        │
                                             └────────────────────────┘

"""

