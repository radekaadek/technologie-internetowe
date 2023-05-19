import socket
import socketserver
import threading
from os import system

HOST = "68.219.96.15"
# HOST = socket.gethostname()
PORT = 8000


class MyTCPHandler(socketserver.BaseRequestHandler):
    # A dictionary that stores the messages for each user
    user_msgs = {}

    def get_user_msgs(self, username: str) -> str:
        msgs = ""
        if username in self.user_msgs and self.user_msgs[username]:
            for msg in self.user_msgs[username]:
                msgs += f"You received a message from {msg[0]}:\n{msg[1]}\n"
            self.user_msgs[username] = []
        return msgs

    def handle(self) -> None:
        # log the user in
        username = self.request.recv(1024).strip().decode("utf-8")
        print(f"User {username} connected")
        print(f"User {self.request.getpeername()} is now online")

        # receive messages from the user
        while True:
            # check if the user received a message
            msg_to_send = bytes(f"""{self.get_user_msgs(username)}
                                \nEnter the recipient: """, "utf-8")

            try:
                self.request.sendall(msg_to_send)
                recipient = self.request.recv(1024).strip().decode("utf-8")
                self.request.sendall(b"Enter your message: ")
                msg = self.request.recv(1024).strip().decode("utf-8")
            except Exception:
                print(f"User {username} disconnected")
                break

            if recipient in self.user_msgs:
                self.user_msgs[recipient].append((username, msg))
            else:
                self.user_msgs[recipient] = [(username, msg)]

            if msg == "exit":
                print(f"User {username} disconnected")
                break
            elif msg:
                print(f"User {username} sent a message to {recipient}")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def runClient() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        msg = input("Enter your username: ")
        sock.connect((HOST, PORT))
        sock.sendall(bytes(msg, "utf-8"))
        while True:
            msg_recv = sock.recv(1024).strip().decode("utf-8")
            # if the message is empty, the server has closed the connection
            if not msg_recv:
                break
            print(msg_recv)
            msg = input()
            while msg == "exit" or msg.strip() == "":
                msg = input("Enter a valid message: ")
            sock.sendall(bytes(msg, "utf-8"))


def startServer() -> None:
    try:
        server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
    except OSError:
        print("A server is already on this address or the address is invalid")
        # kill the program running on the port
        print("Killing the program running on the port")
        # check if the OS is Windows or Linux
        if system("uname") == "Linux":
            system(f"fuser -k {PORT}/tcp")
        elif system("uname") == "Windows":
            system(f"taskkill /F /PID {PORT}")
        else:
            print("System not supported")
        exit(1)

    with server:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("Server started")
        server_thread.join()


if __name__ == "__main__":
    import sys
    file_name = __file__.split("/")[-1]
    if len(sys.argv) < 2:
        print(f"Usage: python3 {file_name} [server|client]")
        exit(1)

    if sys.argv[1] == "server":
        startServer()
    elif sys.argv[1] == "client":
        runClient()
    else:
        print(f"Usage: python3 {file_name} [server|client]")
