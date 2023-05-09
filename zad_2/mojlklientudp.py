# client to mojserverudp.py

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = "68.219.96.15"
port = 8000
s.connect((host, port))
print(s.recv(1024))
s.sendall(b'Witam witam')
s.close()
