import socket

# Create a socket object
s = socket.socket()

host = socket.gethostname()
print(host)

port = 8000

# Bind to the port
s.bind((host, port))

# Now wait for client connection.
s.listen(5)

while True:
    # Establish connection with client.
    c, addr = s.accept()
    print('Got connection from', addr)
    c.send(b'Thank you for connecting')
    c.send(b'Bye')
    # Close the connection
    c.close()

# if the port is still open, you can close it with:
# sudo fuser -k 8000/tcp

