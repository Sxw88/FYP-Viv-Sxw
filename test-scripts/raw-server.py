#!/usr/bin/env python3

import socket

ETH_P_ALL = 3
ETH_FRAME_LEN = 1514 # Max octets in frame sans FCS
interface = "wlan0"

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
s.bind((interface, 0))

while True:
    data = s.recv(ETH_FRAME_LEN)
    print(data)

s.close()
