#!/usr/bin/env python3

#sample code taken from stack overflow forum to scan RSSI of Bluetooth devices nearby

from datetime import datetime
from pathlib import Path
import pydbus
from gi.repository import GLib

discovery_time = 60
log_file = Path('../logs/scan.log')


def write_to_log(address, rssi):
    """Write device and rssi values to a log file"""
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')
    with log_file.open('a') as dev_log:
        dev_log.write(f'Device seen[{current_time}]: {address} @ {rssi} dBm\n')

bus = pydbus.SystemBus()
mainloop = GLib.MainLoop()

class DeviceMonitor:
    """Class to represent remote bluetooth devices discovered"""
    def __init__(self, path_obj):
        self.device = bus.get('org.bluez', path_obj)
        self.device.onPropertiesChanged = self.prop_changed
        rssi = self.device.GetAll('org.bluez.Device1').get('RSSI')
        if rssi:
            print(f'Device added to monitor {self.device.Address} @ {rssi} dBm')
        else:
            print(f'Device added to monitor {self.device.Address}')

    def prop_changed(self, iface, props_changed, props_removed):
        """method to be called when a property value on a device changes"""
        rssi = props_changed.get('RSSI', None)
        if rssi is not None:
            print(f'\tDevice Seen: {self.device.Address} @ {rssi} dBm')
            write_to_log(self.device.Address, rssi)


def end_discovery():
    """method called at the end of discovery scan"""
    mainloop.quit()
    adapter.StopDiscovery()

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

# Iterate around already known devices and add to monitor
print('Adding already known device to monitor...')
mng_objs = mngr.GetManagedObjects()
for path in mng_objs:
    device = mng_objs[path].get('org.bluez.Device1', {}).get('Address', [])
    if device:
        DeviceMonitor(path)

# Run discovery for discovery_time
adapter.StartDiscovery()
GLib.timeout_add_seconds(discovery_time, end_discovery)
print('Finding nearby devices...')
try:
    mainloop.run()
except KeyboardInterrupt:
    end_discovery()
