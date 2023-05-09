# client to server.py
# 89.64.36.207

import socket

# send a packet on port 8000
s = socket.socket()
host = "68.219.96.15"
port = 8000
s.connect((host, port))
print(s.recv(1024))
s.sendall(b'Witam witam')
s.close()
