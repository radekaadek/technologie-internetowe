import socket

host = socket.gethostname()
port = 8000

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((host, port))
    while True:
        data, addr = s.recvfrom(1024)
        print("Received from ", addr)
        print("Received message: ", data.decode())
        s.sendto(b'Witam witam', addr)

# close the socket and free the port with:
# sudo fuser -k 8000/udp
