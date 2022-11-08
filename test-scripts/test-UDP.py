#!/usr/bin/env python3

import sys
sys.path.append("/home/pi/FYP-Viv-Sxw/batman")
from WxAdHocComm import WxAdHocComm

wxCom = WxAdHocComm(client=True)
wxCom.sendUDP("192.168.1.3", "get peers")
