#!/usr/bin/env python3

# Creates a BLE peripheral device

import logging
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

from ble import (
    Advertisement,
    Characteristic,
    Service,
    Application,
    find_adapter,
    Descriptor,
    Agent,
)

import sys
import struct
import array
from enum import Enum

# Set up the mainloop
MainLoop = None
try:
    from gi.repository import GLib
    MainLoop = GLib.MainLoop
except ImportError:
    import gobject as GObject
    MainLoop = GObject.MainLoop

# Set up logging 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
filelogHandler = logging.FileHandler("./logs/peripheral.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
filelogHandler.setFormatter(formatter)
logger.addHandler(filelogHandler)
logger.addHandler(logHandler)

mainloop = None

# Set up names for the BlueZ Service, GATT interface, & Advertisement interface
BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.InvalidValueLength"


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Failed"


def register_app_cb():
    logger.info("GATT application registered")


def register_app_error_cb(error):
    logger.critical("Failed to register application: " + str(error))
    mainloop.quit()

class PiS1Service(Service):
    """
    Dummy test service that provides characteristics and descriptors that
    exercise various API functionality.
    """

    PI_SVC_UUID = "12345678-9abc-def0-1234-56789abcdef0"

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.PI_SVC_UUID, True)
        self.add_characteristic(TestCharacteristic(bus, 0, self))
        self.add_characteristic(StateCharacteristic(bus, 1, self))
        self.add_characteristic(PeersCharacteristic(bus, 2, self))


class TestCharacteristic(Characteristic):
    uuid = "11111111-1111-1111-1111-111111111111"
    #uUID = "12345678-9abc-def0-1234-56789abcdef0"

    description = b"Characteristic to maintain BLE connection - similar to heartbeat protocol"

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.uuid, ["encrypt-read", "encrypt-write"], service,
        )

        self.value = bytearray("Up & Reachable", encoding="utf8")
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        logger.info("read value: " + repr(self.value))
        return self.value

    def WriteValue(self, value, options):        
        #decoded_value = repr(value)
        #logger.info("raw value: " + decoded_value)
        decoded_value = ''.join([str(v) for v in value])
        logger.info("write value: " + decoded_value)

        # Write the value to somewhere
        f = open("output.txt", "w")
        f.write("output:")
        f.write(decoded_value)
        f.close()

        # Change the value of the characteristic
        self.value = value


class StateCharacteristic(Characteristic):
    uuid = "22222222-2222-2222-2222-222222222222"
    description = b"current state of swarm robot"

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.uuid, ["encrypt-read"], service,
        )

        self.value = bytearray("unb", encoding="utf8")
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        """Update the state value and then return value to requester"""
        
        self.value = bytearray("unb", encoding="utf8")

        with open("../state") as f_readstate:
            updated_value = f_readstate.read()
            self.value = bytearray(updated_value[:-1], encoding="utf8")

        logger.info("read value: " + repr(self.value))
        return self.value

    def WriteValue(self, value, options):        
        if not self.writable:
            raise NotPermittedException()
        self.value = value


class PeersCharacteristic(Characteristic):
    uuid = "33333333-3333-3333-3333-333333333333"
    description = b"List of known peers"

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.uuid, ["encrypt-read"], service,
        )

        self.value = bytearray("x", encoding="utf8")
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        """Read the file "known_peers" and then return value to requester"""

        self.value = bytearray("x", encoding="utf8")

        with open("../known_peers") as f_readpeers:
            updated_value = f_readpeers.read()
            self.value = bytearray(updated_value[:-1], encoding="utf8")

        logger.info("read value: " + repr(self.value))
        return self.value

    def WriteValue(self, value, options):        
        if not self.writable:
            raise NotPermittedException()
        self.value = value

class CharacteristicUserDescriptionDescriptor(Descriptor):
    """
    Writable CUD descriptor.
    """

    CUD_UUID = "2901"

    def __init__(
        self, bus, index, characteristic,
    ):

        self.value = array.array("B", characteristic.description)
        self.value = self.value.tolist()
        Descriptor.__init__(self, bus, index, self.CUD_UUID, ["read"], characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value


class PiAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x70, 0x74],
        )
        self.add_service_uuid(PiS1Service.PI_SVC_UUID)
        
        # get local name which is linked to last octet of IP address
        local_name = "Pi-BLE-"
        with open("../info.add") as f_read:
            line_to_read = f_read.readline()
            line_to_read = f_read.readline()
            local_name = local_name + line_to_read[10:-1]
        self.add_local_name(local_name)
        
        self.include_tx_power = True

def register_ad_cb():
    logger.info("Advertisement registered")


def register_ad_error_cb(error):
    logger.critical("Failed to register advertisement: " + str(error))
    mainloop.quit()


AGENT_PATH = "/com/pi/agent"

def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # get the system bus
    bus = dbus.SystemBus()
    # get the ble controller
    adapter = find_adapter(bus)

    if not adapter:
        logger.critical("GattManager1 interface not found")
        return

    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, adapter)

    adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")

    # powered property on the controller to on
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    # Get manager objs
    service_manager = dbus.Interface(adapter_obj, GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

    advertisement = PiAdvertisement(bus, 0)
    obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

    agent = Agent(bus, AGENT_PATH)

    app = Application(bus)
    app.add_service(PiS1Service(bus, 1))

    mainloop = MainLoop()

    agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")

    ad_manager.RegisterAdvertisement(
        advertisement.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    logger.info("Registering GATT application...")

    service_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=[register_app_error_cb],
    )

    agent_manager.RequestDefaultAgent(AGENT_PATH)
    
    mainloop.run()


if __name__ == "__main__":
    main()
