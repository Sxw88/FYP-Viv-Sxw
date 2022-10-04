#!/usr/bin/env python3

#import socket
#import fcntl
#import struct
import os

#def get_ip_address(ifname):
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #return socket.inet_ntoa(fcntl.ioctl(
	#s.fileno(),
	#0x8915, 
	#struct.pack('256s', ifname[:15])
    #)[20:24])

#get_ip_address('bat0')


ipv4 = os.popen('ip addr show bat0').read().split("inet ")[1].split("/")[0]
#ipv6 = os.popen('ip addr show bat0').read().split("inet6 ")[1].split("/")[0]

print(ipv4)

