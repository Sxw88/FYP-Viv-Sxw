#!/usr/bin/env python3

from bluepy import btle
import time

# Match MAC of peripheral
MAC = "dc:a6:32:d3:4f:11"

# Match Service / Characteristic UUID in ble_per.py
SERVICE_UUID = "12345678-9abc-def0-1234-56789abcdef0"
CHARACTERISTIC_UUID = "11111111-1111-1111-1111-111111111111"

nanoRP2040_Char = None

print("Hello World")

print("Connect to:" + MAC)
dev = btle.Peripheral(MAC)
print("\n--- dev ----------------------------")
print(type(dev))
print(dev)

print("\n--- dev.services -------------------")
for svc in dev.services:
    print(str(svc))
    
print("\n------------------------------------")
print("Get Serice By UUID: " + SERVICE_UUID)
service_uuid = btle.UUID(SERVICE_UUID)
service = dev.getServiceByUUID(service_uuid)

print(service)
print("\n--- service.getCharacteristics() ---")
print(type(service.getCharacteristics()))
print(service.getCharacteristics())

#----------------------------------------------
characteristics = dev.getCharacteristics()
print("\n--- dev.getCharacteristics() -------")
print(type(characteristics))
print(characteristics)
    
for char in characteristics:
    print("----------")
    print(type(char))
    print(char)
    print(char.uuid)
    if(char.uuid == CHARACTERISTIC_UUID ):
        print("=== !CHARACTERISTIC_UUID matched! ==")
        nanoRP2040_Char = char
        print(char)
        print(dir(char))
        #print(char.getDescriptors)
        #print(cha  r.propNames)
        #print(char.properties)
        #print(type(char.read()))
        print(char.read())
        
bytes_ON = b'\x01'
bytes_OFF = b'\x00'
msg = "Hello World"
bytes_OFF = bytearray(msg, encoding="utf8")

if nanoRP2040_Char != None:
    print("\nnanoRP2040_Char found")
    print(nanoRP2040_Char)
    for i in range(3):
        nanoRP2040_Char.write(bytes_ON, True)
        print(nanoRP2040_Char.read())
        time.sleep(1.0)
        nanoRP2040_Char.write(bytes_OFF, True)
        print(nanoRP2040_Char.read())
        time.sleep(1.0)
else:
    print("\nnanoRP2040_Char NOT found!")
#=============================================
dev.disconnect()
print("\n--- bye ---\n")
