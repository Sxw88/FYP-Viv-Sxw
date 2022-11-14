#!/usr/bin/env python3

import socket
import os
import re
import logging

logging.basicConfig(level=logging.DEBUG, filename="/home/pi/FYP-Viv-Sxw/batman/udp.log", filemode="a+",format="%(asctime)-15s %(levelname)-8s %(message)s")

class WxAdHocComm:

    def __init__(self, client=False):
        self.batIP = os.popen('ip addr show bat0').read().split("inet ")[1].split("/")[0]

        if client == False:                 # UDP Server is hardcoded to use bat0 interface
            self.localIP = self.batIP 
            logging.info("--------------------- UDP Server Started ----------------------")
        else: 
            self.localIP = "127.0.0.1"      # Client uses the loopback interface
            logging.info("--------------------- UDP Client Started ----------------------")

        self.localPort  = 20001             # hardcoded to use port
        self.bufferSize = 1024              # hardcoded buffer size

        # Create a Datagram socket and bind socket to address & port
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((self.localIP, self.localPort))


    def startServer(self):
        msgFromServer   = "Hello UDP Client. This is a response from UDP Server " + str(self.localIP)
        bytesToSend     = str.encode(msgFromServer)

        print("UDP Server up and listening")

        # Listen for incoming datagrams
        while (True):
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            
            clientMsg = "Message from Client: " + str(message)[2:-1]
            clientIP = "Client IP Address: {}".format(address)
            
            # Print out received info
            print(clientMsg)
            logging.info("\033[1;32mSERVER\033[0m  " + clientMsg)
            print(clientIP)
            logging.info("\033[1;32mSERVER\033[0m  " + clientIP)
            
            # understanding the request of the client 
            request = re.search("@->@(.*?)@<-@", str(message)[2:-1]).group(1)

            # and then crafting an appropriate response           
            response = "Invalid Request"
            if "GET STATE" in request.upper():
                with open("/home/pi/FYP-Viv-Sxw/state", "r") as f_read:
                    response = f_read.readline()
                    response = response[:-1]
            elif "GET PEERS" in request.upper():
                with open("/home/pi/FYP-Viv-Sxw/known_peers", "r") as f_read:
                    response = f_read.readline()
                    if response[-1] == "\n":
                        response = response[:-1]
            elif "TEST" in request.upper():
                response = "Test message received"
            
            msgFromServer = "Hello UDP Client. This is a response from UDP Server " + str(self.localIP)
            msgFromServer += "\n\tRequest : " + request
            msgFromServer += "\n\tResponse: <-<" + response + ">->"
            logging.info("\033[1;34mSERVER RESPONSE\033[0m  " + response)

            # Sending a reply to client
            bytesToSend = str.encode(msgFromServer)
            self.UDPServerSocket.sendto(bytesToSend, address)

    def sendUDP(self, destIP, message):
        msgFromClient       = "Hello UDP Server"
        ip_addr             = self.batIP
        msgFromClient       += " [Source: {}] ".format(ip_addr)
        msgFromClient       += "@->@" + message + "@<-@"

        bytesToSend         = str.encode(msgFromClient)
        serverAddressPort   = (destIP, self.localPort)

        msgFromServer = []
        print("Sent Message: " + msgFromClient)
        logging.info("\033[1;33mCLIENT\033[0m  " + msgFromClient)

        # Create a UDP socket at client side
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as UDPClientSocket:
            # Send to server using created UDP socket
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            msgFromServer = UDPClientSocket.recvfrom(self.bufferSize)
        
        # Rrint out response from the server
        msg = "Response from Server: " + str(msgFromServer[0]).encode("utf-8").decode("unicode_escape")[2:-1]
        print(msg)
        logging.info("\033[1;33mCLIENT\033[0m  " + msg)

        response = re.search("<-<(.*?)>->", msg).group(1)
        return response

if __name__ == "__main__":
	
    # This is NOT test code! 
    # It is used by start-batman-adv.sh to start the UDP server at boot

    wxCom = WxAdHocComm()
    wxCom.startServer()

    # To test the UDP server, use the command as follows:
    # nc -u 192.168.1.x 20001
