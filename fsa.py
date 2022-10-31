#!/usr/bin/env python3

from __future__ import annotations

import time
import json
import sys

from abc import ABC, abstractmethod
from GraphEx import (
        scanRSSI, 
        makeKey, 
        getDistance, 
        estDist,
        getAngletoRefNode, 
        LOCAL_BLE_MAC
        )
from ServoDriver import ServoDriver

sys.path.append("./ble")
from ble_rssi import getJSONData

next_step   = "non"
adist       = 50        # How many centimeters apart between the swarm robots at anchored state
srv         = None      # Servo Driver Object
REF1        = None      # Reference Node 1
REF2        = None      # Reference Node 2

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
        
        # Initialize the Servo Driver object
        global srv
        srv = ServoDriver()
        srv.testCode() # rotate 360 degrees
        
        while next_step == "ini":
            """
                Initialisation loop, will only break under 2 conditions:
                    1) Robot selected for Init-Anchoring process
                    2) More than 2 anchors, proceed to Localize-Triangulate
            """

            # Scan and check for peers which are online
            print("\nScanning for peers (20 seconds):")
            scanRSSI(20)
            
            # Check for any anchored peers from RSSI.json file
            with open("./ble/RSSI.json", "r") as f_rssi:
                RSSI_LIST = json.load(f_rssi)
                ANC_LIST = {}
                IA_LIST = {}

                print("Checking for peers in anchored state:")

                for device in RSSI_LIST:
                    device_state = getJSONData(RSSI_LIST, device, "State")
                    #print("Device MAC: " + str(device) + "\nDevice State: " + str(device_state) + "\n")

                    if device_state == "anc":
                        # Copy the anchored device JSON object to a new list
                        ANC_LIST[device] = {    
                                "Name": getJSONData(RSSI_LIST, device, "Name"),
                                "RSSI": getJSONData(RSSI_LIST, device, "RSSI"),
                                "Last-Seen": getJSONData(RSSI_LIST, device, "Last-Seen")
                                }
                        
                        IA_LIST[device] = {    
                                "Name": getJSONData(RSSI_LIST, device, "Name"),
                                "RSSI": getJSONData(RSSI_LIST, device, "RSSI"),
                                "Last-Seen": getJSONData(RSSI_LIST, device, "Last-Seen")
                                }
                    if device_state == "i-a" or device_state == "i2a":
                        IA_LIST[device] = {    
                                "Name": getJSONData(RSSI_LIST, device, "Name"),
                                "RSSI": getJSONData(RSSI_LIST, device, "RSSI"),
                                "Last-Seen": getJSONData(RSSI_LIST, device, "Last-Seen")
                                }


                print("\nList of Anchored/Anchoring devices")
                print(IA_LIST)
                print(" ")

                if (len(ANC_LIST) >= 2):
                    
                    # End Initialisation state and enter Localization state
                    next_step = "lcl"

                elif (len(IA_LIST) < 2):  # No peers who are in an anchoring state

                    # Enter Initialization-Anchoring state if peers > 0
                    if (len(RSSI_LIST) >= 1): 
                        next_step = "i-a"

                        # Check if this robot has the lowest / second lowest ID (BLE name or static IP address name)
                        
                        # obain the unique ID (which every robot has)
                        unique_ID = "20"
                        with open("info.add") as f_read:
                            line_to_read = f_read.readline()
                            line_to_read = f_read.readline()
                            unique_ID = line_to_read[10:-1]
                        
                        # Get the unique IDs of peer robots from RSSI_LIST
                        smaller_count = 0

                        for device in RSSI_LIST:
                            device_uID = getJSONData(RSSI_LIST, device, "Name")
                            print("Device: " + device_uID)
                            device_uID = device_uID[7:]

                            # Comparison of unique IDs, 
                            # If there are 2 devices which are smaller than the local unique ID,
                            # stay in the initialisation loop

                            print("Comparing ID: Pi-BLE-" + device_uID + " with ID: Pi-BLE-" + unique_ID)

                            if (int(device_uID) < int(unique_ID)):
                                print(device_uID + " is smaller, smaller_count variable +1")
                                smaller_count += 1

                                global REF1
                                REF1 = device

                            else:
                                print(unique_ID + " is smaller")

                        print(" ")

                        if smaller_count >= 2:
                            next_step = "ini"
                            time.sleep(5)
                        elif smaller_count == 1:
                            next_step = "i2a" # Second robot to anchor

                    else:
                        # Stay in Initialisation loop
                        next_step = "ini"
                        print("\033[1;33m[*]\033[0m No peers are online. Script will sleep for 5 seconds and try again.")
                        time.sleep(5)
                else:
                    # Stay in Initialisation loop
                    next_step = "ini"
                    print("\033[1;33m[*]\033[0m Detected peers currently in Init-Anchoring state. Script will sleep for 5 seconds and try again.")
                    time.sleep(5)


    
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

            estDist(7, 5) # scan 7 times for 5 seconds
            rdist1 = getDistance(LOCAL_BLE_MAC, REF1)
            
            # Move a fixed distance (mdist)
            srv.moveStraight(mdist)
            
            # And then determine new distance to the reference node (rdist2)
            rdist2 = rdist1 + mdist + 10        # rdist2 should always be smaller
            while rdist2 > (rdist1 + mdist) or rdist2 < (rdist1 - mdist):    # than the sum of rdist and mdist
                estDist(7, 5) # scan 7 times for 5 seconds
                rdist2 = getDistance(LOCAL_BLE_MAC, REF1) 

            # Attempt clockwise rotation first
            rot = -1
            while rot == -1:
                rot = getAngletoRefNode(rdist1, rdist2, mdist)

                if rot == -1:  # repeat scanning and moving process again
                    print("\033[1;31m[*] Math Error: \033[0m Will proceed to scan again")
                    #scanRSSI(10, fast_mode=True)
                    estDist(7, 5) # scan 7 times for 5 seconds
                    rdist1 = getDistance(LOCAL_BLE_MAC, REF1)

                    # Move a fixed distance (mdist)
                    srv.moveStraight(mdist)
                    
                    # And then determine new distance to the reference node (rdist2)
                    rdist2 = rdist1 + mdist + 10        # rdist2 should always be smaller
                    while rdist2 > (rdist1 + mdist) or rdist2 < (rdist1 - mdist):    # than the sum of rdist and mdist
                        estDist(7, 5) # scan 7 times for 5 seconds
                        rdist2 = getDistance(LOCAL_BLE_MAC, REF1)

            srv.rotateSelf90(rot, clockwise=True)

            # Move forward/backwards x meters to move to desired distance
            mdist = rdist2 - adist
            if mdist < 0:
                srv.moveStraight(0-mdist, backwards=True)
            else:    
                srv.moveStraight(mdist)

            # Scan and Check the new distance
            estDist(7, 5) # scan 7 times for 5 seconds
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
                #scanRSSI(10, fast_mode=True)
                estDist(7, 5) # scan 7 times for 5 seconds
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

    def __init__(self):
        print("\033[1;32m[*]\033[0m Currently in the Localization state")
        # main code for Localization goes here
        global next_step
        next_step = "tte"
    
    # Travel-to-Edge if needed
    def startTTE(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Travel-to-Edge state...")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(TTE())
    
    # Enters Triangulation state if no TTE needed
    def startTriangulation(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Triangulation state...")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Triangulation())

    # Irrelevant states
    def startInitAnchoring(self) -> None:
        print("WARNING: No actions will be carried out")

    def startLocalization(self) -> None:
        print("WARNING: No actions will be carried out")

    def startAnchored(self) -> None:
        print("WARNING: No actions will be carried out")



class TTE(State):

    def __init__(self):
        print("\033[1;32m[*]\033[0m Currently in the Travel-to-Edge (TTE) state")
        # Main code for Travelling-to-Edge process goes here
        global next_step
        next_step = "tri"

    # Enters Triangulation state if TTE successful
    def startTriangulation(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Triangulation state...")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Triangulation())

    # Enters Localization state if TTE is NOT successful
    def startLocalization(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Localization state...")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Localization())

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

    # Enters Localization state if Triangulation is NOT successful
    def startLocalization(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Localization state...")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
        self.fsa.setFSA(Localization())

    # Proceeds to Anchored stateif Triangulation is successful
    def startAnchored(self) -> None:
        print("\033[1;33m[*]\033[0m Switching to the Anchored state...")
        time.sleep(0.3)
        print("*")
        time.sleep(0.3)
        print("*")
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
        # Code for Anchored state goes here
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
        
        #myRobot.presentState()


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

