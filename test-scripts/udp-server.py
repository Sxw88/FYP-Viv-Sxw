#!/usr/bin/env python3

import socket
import os

localIP     = "192.168.1.1"
localPort   = 20001
bufferSize  = 1024

msgFromServer   = "Hello UDP Client"
bytesToSend     = str.encode(msgFromServer)

# Create a Datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and IP
UDPServerSocket.bind((localIP, localPort))

print("UDP Server up and listening")

# Listen for incoming datagrams
while (True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = "Message from Client: {}".format(message)
    clientIP = "Client IP Address: {}".format(address)

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client 
    UDPServerSocket.sendto(bytesToSend, address)
