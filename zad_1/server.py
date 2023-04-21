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
    # Close the connection
    c.close()

