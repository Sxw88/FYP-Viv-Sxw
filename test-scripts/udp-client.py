#!/usr/bin/env python3

import socket
import os

msgFromClient       = "Hello UDP Server"
ip_addr = os.popen('ip addr show bat0').read().split("inet ")[1].split("/")[0]
msgFromClient       += " [Source: {}]".format(ip_addr)

bytesToSend         = str.encode(msgFromClient)
serverAddressPort   = ("192.168.1.1", 20001)
bufferSize          = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)
msgFromServer = UDPClientSocket.recvfrom(bufferSize)


msg = "Message from Server {}".format(msgFromServer[0])
print(msg)
