#!/usr/bin/env python3

import socket

HOST = "192.168.1.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello world")
    data = s.recv(1024)

print(f"Received {data!r}")

