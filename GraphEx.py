#!/usr/bin/env python3

# the module contains various classes / functions
# which are used in the analysis / exchange of the collected RSSI information
# The collected info is read from JSON format, processed and then stored in JSON format


from datetime import datetime
import time
import math
import zlib
import json
import sys

sys.path.append("./ble")
import ble_rssi as blescan
from ble_rssi import getJSONData

sys.path.append("./batman")
from WxAdHocComm import WxAdHocComm

LOCAL_BLE_MAC = "BB:BB:BB:BB:BB:BB"     # Local BLE MAC address (hciconfig)
wxCom = None                # Object which represents the UDP client (Wireless-Communication)
comm_mode = "x"             # Initialize communication mode, BLE or batman-adv

with open("comm_mode") as f:
    comm_mode = f.readline()
    comm_mode = comm_mode[:-1]

    if comm_mode == "bat":
        wxCom = WxAdHocComm(client=True)  # Create wireless adhoc communication object as client
        wxCom.sendUDP(wxCom.batIP, "testing 12345")
    elif comm_mode != "ble" and comm_mode != "bat":
        comm_mode = "ble"       # if communication mode not found default to BLE
        f.write("ble\n")
        print("[*] Communication mode not found in ./comm_mode, defaulting to BLE.")
    print("Current Communication Mode: " + comm_mode)

with open('info.add', 'r') as f:
    LOCAL_BLE_MAC = f.readline()
    LOCAL_BLE_MAC = f.readline()
    LOCAL_BLE_MAC = f.readline()
    LOCAL_BLE_MAC = LOCAL_BLE_MAC[:-1].upper()
    print(f"Local BLE/WLAN MAC Address: {LOCAL_BLE_MAC}")


def makeKey(node1, node2):
    # CRC32 hash function is used to shorten the unique key
    # formed by the combination of MAC addresses of nodes.

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
        theta = math.degrees(math.acos(var_x))
        theta = 180 - theta
        return int(theta)
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
    n = 4.0
    L = 6

    x = math.log(10, math.e) * ((P0-rssi)/(10*n))
    y = 1

    for i in range(1, L+1):
        y += pow(x, i) / factorial(i)

    d = d0 * y
    d = round(d, 2)

    return d


def scanRSSI(timeout, fast_mode=False, verbose=True):
    """Scan RSSI of nearby BLE devices, and save info in JSON
        * fast_mode when set to False will get the state of the peers
    """

    # check the comm_mode variable, to decide which method to use to get state of other robots
    global comm_mode
    global wxCom

    if comm_mode == "ble":
        blescan.runscan(timeout, -80, fast_mode=fast_mode, verbose=verbose)
        time.sleep(0.5)         # sleep for a while to avoid race condition
    elif comm_mode == "bat":
        blescan.runscan(timeout/2, -80, fast_mode=True, verbose=verbose)
        time.sleep(0.5)         # sleep for a while to avoid race condition
        if fast_mode == False:
            # Scan and check for peers who are online
            with open("./ble/RSSI.json", "r") as f_read:
                DEVICES_LIST = json.load(f_read)
                for device in DEVICES_LIST:
                    device_uID = DEVICES_LIST[device]["Name"][7:]
                    device_state = wxCom.sendUDP("192.168.1."+device_uID, "GET STATE")
                    DEVICES_LIST[device]["State"] = device_state

            # save file back to RSSI.json
            with open("./ble/RSSI.json", "w") as f_write:
                json.dump(DEVICES_LIST, f_write, indent=2)

    # read results of scan from JSON file format
    RSSI_LIST = []
    with open("ble/RSSI.json", 'r') as read_file:
        RSSI_LIST = json.load(read_file)

    # format each device in a new JSON list with distance conversion
    NEW_LIST = []
    with open("GRAPH.json", 'r') as read_file:
        NEW_LIST = json.load(read_file)

    for device in RSSI_LIST:
        if device in blescan.SCANNED_HOSTS:

            if verbose:
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


def estDist(rep, timeout, verbose=False, target_MAC=None):
    """estimate distance to neighbouring nodes by scanning RSSI repeatedly and getting the average value"""

    print("\033[1;32m[*]\033[0m Scanning " + str(rep) + " times for " + str(timeout) + " seconds each.")

    i = 0
    while i < rep:
        # read distance (weight) from GRAPH.json
        GLIST1 = []
        i = i +1

        with open("GRAPH.json", 'r') as read_file:
            GLIST1 = json.load(read_file)

        scanRSSI(timeout, fast_mode=True, verbose=False)
        print("Round " + str(i) + " - List of Scanned Hosts: " + str(blescan.SCANNED_HOSTS))

        if target_MAC != None and target_MAC not in blescan.SCANNED_HOSTS:
            print("\033[31mTarget did not show up in previous scan... \033[0mScan will be repeated one more time.")
            i = i - 1
            time.sleep(1)
        else:
            # read distance (weight) from GRAPH.json again after scanning
            GLIST2 = []
            with open("GRAPH.json", 'r') as read_file:
                GLIST2 = json.load(read_file)

            for device_hash in GLIST1:
                try:
                    read_dist = GLIST1[device_hash]["weight"]
                    GLIST1[device_hash]["weight"] = round((read_dist*(i-1) + GLIST2[device_hash]["weight"]) / (i), 2)
                    if target_MAC == None or device_hash == makeKey(target_MAC, LOCAL_BLE_MAC):

                        if target_MAC == None:
                            device = " No device "
                            if GLIST1[device_hash]["MAC-1"] == LOCAL_BLE_MAC.upper():
                                device = GLIST1[device_hash]["MAC-2"]
                            else:
                                device = GLIST1[device_hash]["MAC-1"]
                            print("\033[1;36m-- Device: " + device + " --\033[0m")

                        else:
                            print("\033[1;36m-- Device: " + target_MAC + " --\033[0m")

                        #print("Read Value     (distance) : " + str(read_dist) + " meters")
                        #print("Updated Value  (distance) : " + str(GLIST1[device_hash]["weight"]) + " meters")
                        print("Read Value\t\tMeasured Value\t\tUpdated Value")
                        print( str(read_dist) + "\t\t\t" + str(GLIST2[device_hash]["weight"]) + "\t\t\t" + str(GLIST1[device_hash]["weight"]) )
                except:
                    print("\033[1;31m[!] Error:\033[0m Distance not recorded for device + " + str(device))

            # Write JSON data to file
            with open('GRAPH.json', 'w') as output_file:
                json.dump(GLIST1, output_file, indent=2)
                print("saved updated value to GRAPH.json file")



if __name__ == "__main__":

    print("Hello World. This is a test on the communication module")
    #MAC1 = "53-02-16-1C-23-E5"
    #MAC2 = "F5-B9-EB-C9-B9-8C"

    #print(makeKey(MAC1, MAC2))
    #print(makeKey(MAC2, MAC1))


    # Read MAC from device info.add
    #with open("info.add") as f:
    #    MAC1 = f.readline()
    #    MAC1 = f.readline()
    #    MAC1 = f.readline()
    #    MAC1 = MAC1[:-1]

    #print(MAC1)
    #MAC2 = "DC:A6:32:D3:4F:11"

    #G_LIST = []
    #with open("GRAPH.json") as f:
    #    G_LIST = json.load(f)
    #    print(G_LIST)

    #print(makeKey(MAC1, MAC2))
    #print(getJSONData(G_LIST, makeKey(MAC1,MAC2), "weight"))

    #print("\n\n\n\n\n\n\n")
    #estDist(10,2, target_MAC="DC:A6:32:D3:4F:11") # scan 3 times for 5 secs
