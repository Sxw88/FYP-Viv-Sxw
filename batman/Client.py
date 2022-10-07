#!/usr/bin/env python3

import AdHocComm as ac

newUDPClient = ac.AdHocComm()

jsonData = {
	"key1" : "Hello",
	"key2" : "World",
	"key3" : 888,
	"key4" : {"123" : 456, "testing" : 123}
    }

newUDPClient.sendUDP("192.168.1.2", str(jsonData))
#newUDPClient.sendUDP("192.168.1.2", str(jsonData))
#newUDPClient.sendUDP("192.168.1.2", str(jsonData))
