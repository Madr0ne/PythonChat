import socket
import threading
import sys
import time
from random import randint

SOCKET = 50001


def update_peers(peer_data):
    p2p.peers = str(peer_data, 'utf-8').split(",")[:-1]


class Server:
    connections = []

    def send_msg(self, sock):
        while True:
            message = name + ': ' + input("")
            print(message)
            for connection in self.connections:
                connection.send(bytes(message, 'utf-8'))

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', SOCKET))
        sock.listen(1)
        print("Server running")
        print(p2p.peers)
        iThread = threading.Thread(target=self.send_msg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            p2p.peers.append(a[0])
            print(p2p.peers)
            print(str(a[0]) + ':' + str(a[1]), " connected.")
            self.send_peers()

    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            print(str(data, 'utf-8'))
            for connection in self.connections:
                connection.send(data)
                if data[
                   0:1] == b'\x11':  # Leading first bytes object signifies that an updated list of peers is received
                    update_peers(data[1:])
            if not data:
                print(str(a[0]) + ':' + str(a[1]), " disconnected.")
                self.connections.remove(c)
                p2p.peers.remove(a[0])
                c.close()
                self.send_peers()
                break

    def send_peers(self):
        p = ""
        for peer in p2p.peers:
            p = p + peer + ","

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, 'utf-8'))  # Send updated peers with leading bytes object


class Client:
    def send_msg(self, sock):
        while True:
            sock.send(bytes((name + ': ' + input("")), 'utf-8'))

    def __init__(self, address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, SOCKET))
        print('Connected to', address)
        iThread = threading.Thread(target=self.send_msg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:
            data = sock.recv(1024)
            if not data:
                break
            if data[0:1] == b'\x11':
                update_peers(data[1:])
            else:
                print(p2p.peers)
                print(str(data, 'utf-8'))


class p2p:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = str(s.getsockname()[0])
    print(IP)
    peers = [IP]


name = input("Enter your name:")

while True:
    try:
        print("Trying to connect...")
        time.sleep(randint(1, 3))
        for peer in p2p.peers:
            try:
                client = Client(peer)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass
            if True:
                print("Trying to start the server...")
                try:
                    server = Server()
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print("Couldn't start the server...")
    except KeyboardInterrupt:
        sys.exit(0)
