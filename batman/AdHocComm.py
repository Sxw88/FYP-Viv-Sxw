#!/usr/bin/env python3

import socket
import os

class AdHocComm:

    def __init__(self):
        self.localIP = os.popen('ip addr show bat0').read().split("inet ")[1].split("/")[0]
                                            # hardcoded to use bat0 interface
        self.localPort  = 20001             # hardcoded to use port 
        self.bufferSize = 1024              # hardcoded buffer size

        # Create a Datagram socket and bind socket to address & port
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((self.localIP, self.localPort))


    def startServer(self):
        msgFromServer   = "Hello UDP Client. This is a response from UDP Server. All is well."
        bytesToSend     = str.encode(msgFromServer)

        print("UDP Server up and listening")

        # Listen for incoming datagrams
        while (True):
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]

            clientMsg = "Message from Client: {}".format(message)
            clientIP = "Client IP Address: {}".format(address)

            print(clientMsg)
            print(clientIP)

            # Sending a reply to client 
            self.UDPServerSocket.sendto(bytesToSend, address)
    
    def sendUDP(self, destIP, message):
        msgFromClient       = "Hello UDP Server"
        ip_addr             = self.localIP
        msgFromClient       += " [Source: {}] ".format(ip_addr)
        msgFromClient       += "@->@" + message + "@<-@"

        bytesToSend         = str.encode(msgFromClient)
        serverAddressPort   = (destIP, self.localPort)

        msgFromServer = []
        
        # Create a UDP socket at client side
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            # Send to server using created UDP socket
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            msgFromServer = UDPClientSocket.recvfrom(self.bufferSize)

        msg = "Message from Server {}".format(msgFromServer[0])
        print(msg)

if __name__ == "__main__":
    newUDP = AdHocComm()
    newUDP.startServer()

