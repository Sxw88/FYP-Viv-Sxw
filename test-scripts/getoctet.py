#!/usr/bin/env python3

print("This script gets the last octet of the static IP address in info.add")

with open("../info.add") as f:
    line1 = f.readline()
    line2 = f.readline()
    print(line2[10:-1])
