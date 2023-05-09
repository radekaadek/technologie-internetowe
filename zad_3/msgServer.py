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

class MyTCPHandler(socketserver.BaseRequestHandler):
    # A dictionary that stores the messages for each user
    user_msgs = {}
    
    def handle(self):
        # log the user in
        username = self.request.recv(1024).strip().decode("utf-8")
        print("User {} connected".format(username))

        # send the user their messages
        if username in self.user_msgs:
            for msg in self.user_msgs[username]:
                self.request.sendall(bytes("You have a message from {}: {}\n".format(msg[0], msg[1]), "utf-8"))
            self.user_msgs[username] = []
        
        # receive messages from the user
        while True:
            # check if the user received a message
            msg_to_send = ""
            if username in self.user_msgs:
                for msg in self.user_msgs[username]:
                    msg_to_send += "You have a message from {}: {}\n".format(msg[0], msg[1])
                self.user_msgs[username] = []
            msg_to_send = bytes(msg_to_send + "Enter the recipient: ", "utf-8")
            self.request.sendall(msg_to_send)
            try:
                recipient = self.request.recv(1024).strip().decode("utf-8")
                self.request.sendall(b"Enter your message: ")
                msg = self.request.recv(1024).strip().decode("utf-8")
            except Exception:
                print("User {} disconnected".format(username))
                break
            if recipient in self.user_msgs:
                self.user_msgs[recipient].append((username, msg))
            else:
                self.user_msgs[recipient] = [(username, msg)]
            print("User {} sent a message to {}".format(username, recipient))


def client():
    HOST, PORT = "localhost", 9999

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
            sock.sendall(bytes(msg, "utf-8"))



def server():
    HOST, PORT = "localhost", 9999

    # Check if the Address is already in use
    # if it is, kill the process
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((HOST, PORT))
    except OSError:
        print("Address already in use")
        exit(1)
    
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    import sys
    if sys.argv[1] == "client":
        client()
    elif sys.argv[1] == "server":
        server()
    else:
        print("Usage: python3 msgServer.py [client|server]")
