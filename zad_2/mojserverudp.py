# simple udp server

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostname()
port = 8000
s.bind((host, port))

while True:
    data, addr = s.recvfrom(1024)
    print("Received from ", addr)
    print("Received message: ", data.decode())
    s.sendto(b'Witam witam', addr)
    s.close()
    