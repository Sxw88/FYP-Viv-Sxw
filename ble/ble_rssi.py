#!/usr/bin/env python3

# Scans nearby BLE devices, Gets the RSSI value,
# and then stores the device address, RSSI, along 
# with other information in JSON format


from datetime import datetime
from pathlib import Path
import pydbus
from gi.repository import GLib
import json
from ble_cen import readCharacteristic

log_file        = Path('/home/pi/FYP-Viv-Sxw/ble/logs/scan.log')
RSSI_THRESHOLD  = -90       # Not actually used
SERVICE_UUID    = "12345678-9abc-def0-1234-56789abcdef0"
SCAN_FAST_MODE  = False
SCAN_SHOW_ALL   = False
VERBOSE_MODE    = True
SCANNED_HOSTS   = []        # List of hosts which appeared in a scan

def write_to_log(address, rssi):
    """Write device and rssi values to a log file"""
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')
    with log_file.open('a') as dev_log:
        dev_log.write(f'\033[32mDevice seen[{current_time}]: {address} @ {rssi} dBme\033[0m\n')

def getJSONData(J_LIST, BLE_MAC, key):
    """Gets JSON Data from List"""
    try:
        return J_LIST[BLE_MAC][key]
    except KeyError:
        print("\033[1;31mKey Error:\033[0m Device with specified MAC does not exist")


def saveInfo_RSSI(J_LIST, BLE_MAC, field_name, field_RSSI):
    """Appends JSON data to list"""
    
    json_list = J_LIST
    timestamp = datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
    
    state = "unk"
    # get the state from the swarm robot
    if SCAN_FAST_MODE == False:
        try:
            CHARACTERISTIC_UUID = "22222222-2222-2222-2222-222222222222"
            state = readCharacteristic(BLE_MAC, SERVICE_UUID, CHARACTERISTIC_UUID)
        except:
            print("\033[1;31mError:\033[0m Unable to read state of swarm robot")

    # New Key-Value pair added to JSON_LIST
    # Using the Bluetooth MAC as the unique key
    json_list[BLE_MAC] = {
            "Name":field_name, 
            "RSSI":field_RSSI, 
            "State":state, 
            "Last-Seen":timestamp
            }

    return json_list
   
def update_RSSI(J_LIST, BLE_MAC, key, new_value):
    """Sets JSON value given key and index"""
    json_list = J_LIST
    obj_count = 0
    timestamp = datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
    
    state = "unk"

    # get the state from the swarm robot
    if SCAN_FAST_MODE == False and getJSONData(json_list, BLE_MAC, "State") != "anc":
        # Query the current mode via BT central client
        try:
            CHARACTERISTIC_UUID = "22222222-2222-2222-2222-222222222222"
            state = readCharacteristic(BLE_MAC, SERVICE_UUID, CHARACTERISTIC_UUID)
        except:
            print("\033[1;31mError:\033[0m Unable to read state of swarm robot")
    else:
        # Else maintain current state
        state = getJSONData(json_list, BLE_MAC, "State")

    try:
        json_list[BLE_MAC][key] = new_value
        json_list[BLE_MAC]["Last-Seen"] = timestamp 
        json_list[BLE_MAC]["State"] = state
    except KeyError:
        print("\033[1;31mKey Error:\033[0m Device with specified MAC does not exist. Value not updated.")

    return json_list

# read the JSON file and store contents in a list
JSON_LIST = []
with open('/home/pi/FYP-Viv-Sxw/ble/RSSI.json', 'r') as read_file:
        JSON_LIST = json.load(read_file)

bus = pydbus.SystemBus()
mainloop = GLib.MainLoop()

class DeviceMonitor:
    """Class to represent remote bluetooth devices discovered"""

    def __init__(self, path_obj):
        
        global JSON_LIST
        global SCAN_SHOW_ALL
        global SCANNED_HOSTS

        self.device_id = len(JSON_LIST)

        self.device = bus.get('org.bluez', path_obj)
        self.device.onPropertiesChanged = self.prop_changed
        rssi = self.device.GetAll('org.bluez.Device1').get('RSSI')
        
        self.ori_name = self.device.GetAll('org.bluez.Device1').get('Name')
        if self.ori_name == None:
            self.ori_name = "Nameless-Device"
        self.device_name = "Device-Default-Name"
        
        if SCAN_SHOW_ALL == True or self.ori_name != "Nameless-Device": 
            if rssi is not None and int(rssi) > RSSI_THRESHOLD:
                if self.device.Address in JSON_LIST:
                    self.device_name = '\033[1;33m' + JSON_LIST[self.device.Address]["Name"] + '\033[0m'
                    if VERBOSE_MODE:
                        print(f"MAC Address Already Exists. {self.device_name} ({self.ori_name}) added to monitor {self.device.Address} @ {rssi} dBm")
                    if self.device.Address not in SCANNED_HOSTS:
                        SCANNED_HOSTS.append(self.device.Address)
                else:
                    self.device_name = '\033[1;33m' + "BLE-Device-" + str(self.device_id)  + '\033[0m'
                    if VERBOSE_MODE:
                        print(f'\033[1;32mNEW: \033[0m{self.device_name} ({self.ori_name}) added to monitor {self.device.Address} @ {rssi} dBm')
                    if "Pi-BLE" in self.ori_name:
                        if VERBOSE_MODE:
                            print("\t:Device saved.")
                        if self.device.Address not in SCANNED_HOSTS:
                            SCANNED_HOSTS.append(self.device.Address)
                        JSON_LIST = saveInfo_RSSI(JSON_LIST, self.device.Address, self.ori_name, rssi)


    def prop_changed(self, iface, props_changed, props_removed):
        """method to be called when a property value on a device changes"""
        
        global JSON_LIST
        global SCAN_SHOW_ALL
        global SCANNED_HOSTS

        rssi = props_changed.get('RSSI', None)
        
        if SCAN_SHOW_ALL == True or self.ori_name != "Nameless-Device":
            if rssi is not None and int(rssi) > RSSI_THRESHOLD:
                if self.device.Address in JSON_LIST:
                    self.device_name = '\033[1;33m' + JSON_LIST[self.device.Address]["Name"] + '\033[0m'
                    if VERBOSE_MODE:    
                        print(f'\t\033[32mDevice Seen: \033[0m {self.device_name} ({self.ori_name}) at address: {self.device.Address} @ {rssi} dBm')
                    write_to_log(self.device.Address, rssi)
                    if self.device.Address not in SCANNED_HOSTS:
                        SCANNED_HOSTS.append(self.device.Address)
                    JSON_LIST = update_RSSI(JSON_LIST, self.device.Address, "RSSI", rssi)
                else:
                    self.device_id = len(JSON_LIST)
                    self.device_name = '\033[1;33m' + "BLE-Device-" + str(self.device_id)  + '\033[0m'  
                    if VERBOSE_MODE:
                        print(f'\033[1;32mNEW Device Seen: \033[0m {self.device_name} ({self.ori_name}) at address: {self.device.Address} @ {rssi} dBm')
                    if "Pi-BLE" in self.ori_name:
                        if VERBOSE_MODE:
                            print("\t:Device saved.")
                        if self.device.Address not in SCANNED_HOSTS:
                            SCANNED_HOSTS.append(self.device.Address)
                        JSON_LIST = saveInfo_RSSI(JSON_LIST, self.device.Address, self.ori_name, rssi)


def end_discovery():
    """method called at the end of discovery scan"""
    mainloop.quit()
    adapter.StopDiscovery()

    # Write JSON data to file
    with open('/home/pi/FYP-Viv-Sxw/ble/RSSI.json', 'w') as output_file:
        json.dump(JSON_LIST, output_file, indent=2)

def new_iface(path, iface_props):
    """If a new dbus interfaces is a device, add it to be  monitored"""
    device_addr = iface_props.get('org.bluez.Device1', {}).get('Address')
    if device_addr:
        DeviceMonitor(path)

# BlueZ object manager
mngr = bus.get('org.bluez', '/')
mngr.onInterfacesAdded = new_iface

# Connect to the DBus api for the Bluetooth adapter
adapter = bus.get('org.bluez', '/org/bluez/hci0')
adapter.DuplicateData = False


def startScan():
    
    # Iterate around already known devices and add to monitor
    print('Adding already known device to monitor...')
    mng_objs = mngr.GetManagedObjects()
    for path in mng_objs:
        device = mng_objs[path].get('org.bluez.Device1', {}).get('Address', [])
        if device:
            DeviceMonitor(path)


def runscan(discovery_time, rssi_threshold, fast_mode=False, show_all=False, verbose=True):

    global RSSI_THRESHOLD
    RSSI_THRESHOLD = rssi_threshold

    global SCAN_FAST_MODE
    SCAN_FAST_MODE = fast_mode

    global SCAN_SHOW_ALL
    SCAN_SHOW_ALL = show_all

    global VERBOSE_MODE
    VERBOSE_MODE = verbose

    global SCANNED_HOSTS
    SCANNED_HOSTS = []

    # Run discovery for discovery_time
    adapter.StartDiscovery()
    GLib.timeout_add_seconds(discovery_time, end_discovery)
    print('\nFinding nearby devices... (' + str(discovery_time) + " seconds)")

    try:
        mainloop.run()
    except KeyboardInterrupt:
        end_discovery()

startScan()

if __name__ == "__main__":
    runscan(5, -90, fast_mode=True)
    runscan(5, -90, fast_mode=True)


