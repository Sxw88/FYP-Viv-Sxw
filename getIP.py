#!/usr/bin/python

from scapy.all import send, srp, Ether, ARP 

pkt = Ether(dst="dc:a6:32:d3:4f:10")/ARP(pdst="169.254.0.0/16")
ans,unans = send(pkt)

ip = ans[0][1][ARP].hwsrc
print(ip)

