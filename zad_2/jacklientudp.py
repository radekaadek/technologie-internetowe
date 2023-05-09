import socket

host = "68.219.96.15"
port = 8000

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b'Hola Hola!', (host, port))
    data, addr = s.recvfrom(1024)
    print("Received from ", addr)
    print("Received message: ", data.decode())
