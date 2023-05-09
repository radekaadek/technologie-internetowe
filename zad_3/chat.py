# Komunikator internetowy
# Celem ćwiczenia jest implementacja komunikatora internetowego używającego protokołu TCP.
# Opis:
# 1. Należy zaimplementować serwer oraz klienta.
# 2. Komunikator nie wymaga autentykacji.
# 3. Klient i serwer uruchomiane są z linii poleceń.
# 4. Należy założyć, że każdy użytkownik ma przypisany nick. Użytkownicy nie rejestrują się, nie
# podkradają wiadomości innym. Zakładamy dobrą wolę i współpracę użytkowników.
# 5. Klient wysyła do serwera komunikat przeznaczony dla innego użytkownika.
# 6. Klient powinien przysłać komunikat z informacją o nicku nadawcy i odbiorcy.
# 7. Serwer odbiera komunikat od klienta.
# 8. Serwer przechowuje komunikaty w pamięci, nie musi ich trwale zapisywać. Jeśli zostanie
# wyłączony, trudno, niedostarczone wiadomości zostaną zgubione.
# 9. Klient po uruchomieniu odbiera wiadomości z serwera przeznaczone dla niego. Powinien
# również odbierać wiadomości przed wysłaniem swoich.
# 10. Serwer wysyła wiadomości razem z nickami nadawców.
# 11. Serwer powinien trzymać niedostarczone wiadomości w liście obiektów lub krotek
# (nadawca, odbiorca, wiadomość). Lepsze (o lepszej złożoności czasowej) jest jednak
# trzymanie tablicy asocjacyjnej (w Pythonie dictionary/słownik) indeksowanej przez
# odbiorcę i zwierającej listę obiektów lub krotek (nadawca, wiadomość).
# 12. Aby zrealizować komunikację należy zaprojektować własny protokół, który umożliwia
# wysyłanie i odbierania wiadomości z serwera. Potrzebny będą komunikaty:
# a. Sprawdzenie i pobranie wiadomości dla danego użytkownika.
# b. Wysłanie wiadomości do innego użytkownika.
# c. Przesłanie klientowi jego widomości.

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


def client() -> None:
    msg = input("Enter your username: ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
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


def server() -> None:
    try:
        server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
    except OSError:
        print("A server is already on this address or the address is invalid")
        # kill the program running on the port
        print("Killing the program running on the port")
        system(f"fuser -k {PORT}/tcp")

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
        server()
    elif sys.argv[1] == "client":
        client()
    else:
        print(f"Usage: python3 {file_name} [server|client]")
