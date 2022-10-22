#!/usr/bin/env python3

from bluepy import btle
import time

def vprint(string_to_print, v=False):
    if v:
        print(string_to_print)

def writeCharacteristic(MAC, SERVICE_UUID, CHARACTERISTIC_UUID, TO_WRITE, verbose=False):
    
    print("\tWriting to BLE device at MAC Address : " + MAC)
    print("\twith service UUID                    : " + SERVICE_UUID)
    print("\tand with characteristic UUID         : " + CHARACTERISTIC_UUID)

    read_Char = None
    
    vprint("Connect to:" + MAC, v=verbose)
    dev = btle.Peripheral(MAC)
    vprint("\n--- dev ----------------------------", v=verbose)
    vprint(type(dev), v=verbose)
    vprint(dev, v=verbose)

    vprint("\n--- dev.services -------------------", v=verbose)
    for svc in dev.services:
        vprint(str(svc), v=verbose)
        
    vprint("\n------------------------------------", v=verbose)
    vprint("Get Service By UUID: " + SERVICE_UUID, v=verbose)
    service_uuid = btle.UUID(SERVICE_UUID)
    service = dev.getServiceByUUID(service_uuid)

    vprint(service, v=verbose)
    vprint("\n--- service.getCharacteristics() ---", v=verbose)
    vprint(type(service.getCharacteristics()), v=verbose)
    vprint(service.getCharacteristics(), v=verbose)

    #----------------------------------------------
    characteristics = dev.getCharacteristics()
    vprint("\n--- dev.getCharacteristics() -------", v=verbose)
    vprint(type(characteristics), v=verbose)
    vprint(characteristics, v=verbose)
        
    for char in characteristics:
        vprint("----------", v=verbose)
        vprint(type(char), v=verbose)
        vprint(char, v=verbose)
        vprint(char.uuid, v=verbose)
        if(char.uuid == CHARACTERISTIC_UUID ):
            vprint("=== !CHARACTERISTIC_UUID matched! ==", v=verbose)
            read_Char = char
            vprint(char, v=verbose)
            #print(dir(char))
            #print(char.getDescriptors)
            #print(cha  r.propNames)
            #print(char.properties)
            #print(type(char.read()))
            #print(char.read())
        
    bytes_to_write = bytearray(TO_WRITE, encoding="utf8")

    if read_Char != None:
        vprint("\nCharacteristic found. Attempting to write now.", v=verbose)
        vprint(read_Char, v=verbose)
        read_Char.write(bytes_to_write, True)
        #print(read_Char.read())
        time.sleep(1.0)
        print("\033[1;33m(*) \033[0m Wrote to characteristic with message: " + TO_WRITE)
    else:
        print("\n\033[1;31[!] \033[0mSpecified Characteristic NOT found!")
    #=============================================
    dev.disconnect()
    vprint("\n--- bye ---\n", v=verbose)


def checkService(MAC, SERVICE_UUID, verbose=False):

    print("\tConnecting to BLE device at MAC Address : " + MAC)
    print("\tChecking for Service with UUID          : " + SERVICE_UUID)
    
    try:
        dev = btle.Peripheral(MAC)
        vprint("\n--- dev ----------------------------", v=verbose)
        vprint(type(dev), v=verbose)
        vprint(dev, v=verbose)

        vprint("\n--- dev.services -------------------", v=verbose)
        for svc in dev.services:
            vprint(str(svc), v=verbose)
            
        vprint("\n------------------------------------", v=verbose)
        vprint("Get Service By UUID: " + SERVICE_UUID, v=verbose)
        service_uuid = btle.UUID(SERVICE_UUID)
        try:
            service = dev.getServiceByUUID(service_uuid)
            vprint(service.uuid, v=verbose)
            print("\033[1;32m[*] \033[0mService found." )
            return True
        except:
            print("\033[1;31mException: \033[0mCan't find service with UUID: " + SERVICE_UUID)
            return False
    except:
        print("\033[1;31mException: \033[0mCan't connect to device: " + MAC)
        return False


def readCharacteristic(MAC, SERVICE_UUID, CHARACTERISTIC_UUID, verbose=False):
    print("\tReading from BLE device at MAC Address : " + MAC)
    print("\twith service UUID                      : " + SERVICE_UUID)
    print("\tand with characteristic UUID           : " + CHARACTERISTIC_UUID)

    read_Char = None
    
    vprint("Connect to:" + MAC, v=verbose)
    dev = btle.Peripheral(MAC)
    vprint("\n--- dev ----------------------------", v=verbose)
    vprint(type(dev), v=verbose)
    vprint(dev, v=verbose)

    vprint("\n--- dev.services -------------------", v=verbose)
    for svc in dev.services:
        vprint(str(svc), v=verbose)
        
    vprint("\n------------------------------------", v=verbose)
    vprint("Get Service By UUID: " + SERVICE_UUID, v=verbose)
    service_uuid = btle.UUID(SERVICE_UUID)
    service = dev.getServiceByUUID(service_uuid)

    vprint(service, v=verbose)
    vprint("\n--- service.getCharacteristics() ---", v=verbose)
    vprint(type(service.getCharacteristics()), v=verbose)
    vprint(service.getCharacteristics(), v=verbose)

    #----------------------------------------------
    characteristics = dev.getCharacteristics()
    vprint("\n--- dev.getCharacteristics() -------", v=verbose)
    vprint(type(characteristics), v=verbose)
    vprint(characteristics, v=verbose)
        
    read_value = ""
    
    for char in characteristics:
        vprint("----------", v=verbose)
        vprint(type(char), v=verbose)
        vprint(char, v=verbose)
        vprint(char.uuid, v=verbose)
        if(char.uuid == CHARACTERISTIC_UUID ):
            vprint("=== !CHARACTERISTIC_UUID matched! ==", v=verbose)
            read_Char = char
            vprint(char, v=verbose)
            #print(dir(char))
            #print(char.getDescriptors)
            #print(char.propNames)
            #print(char.properties)
            #print(type(char.read()))
            read_value = str(char.read())
            read_value = read_value[2:-1]
            print("\t\tRead characteristic: " + read_value)

        #=============================================
    
    dev.disconnect()
    vprint("\n--- bye ---\n", v=verbose)
    return read_value

if __name__ == "__main__":
    # Match MAC of peripheral
    MAC = "dc:a6:32:d3:4f:11"

    # Match Service / Characteristic UUID in ble_per.py
    SERVICE_UUID = "12345678-9abc-def0-1234-56789abcdef0"
    CHARACTERISTIC_UUID = "11111111-1111-1111-1111-111111111111"
    CHARACTERISTIC_UUID = "22222222-2222-2222-2222-222222222222"

    MESSAGE = "HELLO EARTHLINGS WE CXME IN PEACE"
    
    # Test write function
    #writeCharacteristic(MAC, SERVICE_UUID, CHARACTERISTIC_UUID, MESSAGE, verbose=True)

    # Test check service function
    #print(checkService(MAC, SERVICE_UUID, verbose=True))

    # Test readCharacteristic function
    readCharacteristic(MAC, SERVICE_UUID, CHARACTERISTIC_UUID, verbose=True )
