# send a packet to soc.py

import socket

# send a packet on port 8000
s = socket.socket()
host = "68.219.96.15"
port = 8000
s.connect((host, port))
print(s.recv(1024))
s.close()
