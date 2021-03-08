import socket
import threading
import sys
import time
from random import randint
import ipaddress


class Server:
    connections = []
    peers = []

    def send_msg(self, sock):
        while True:
            message = input("")
            print(message)
            for connection in self.connections:
                connection.send(bytes(message, 'utf-8'))



    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 10001))
        sock.listen(1)
        print("Server running...")
        iThread = threading.Thread(target=self.send_msg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0])
            print(str(a[0]) + ':' + str(a[1]), " connected.")
            self.send_peers()

    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            print(str(data, 'utf-8'))
            for connection in self.connections:
                connection.send(data)
                if data[0:1] == b'\x11':
                    self.update_peers(data[1:])
            if not data:
                print(str(a[0]) + ':' + str(a[1]), " disconnected.")
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.send_peers()
                break

    def send_peers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, 'utf-8'))


class Client:
    def send_msg(self, sock):
        while True:
            sock.send(bytes(input(""), 'utf-8'))

    def __init__(self, address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, 10001))
        print('Connected to', address)
        iThread = threading.Thread(target=self.send_msg, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:
            data = sock.recv(1024)
            if not data:
                break
            if data[0:1] == b'\x11':
                self.update_peers(data[1:])
            else:
                print(str(data, 'utf-8'))

    def update_peers(self, peer_data):
        p2p.peers = str(peer_data, 'utf-8').split(",")[:-1]


class p2p:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = str(s.getsockname()[0])
    print(IP)
    peers = [IP]

while True:
    try:
        print("Trying to connect...")
        time.sleep(randint(1, 3))
        for peer in p2p.peers:
            try:
                client = Client(ipaddress.broadcast_address)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass

            if True:
                try:
                    server = Server()
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print("Couldn't start the server...")
    except KeyboardInterrupt:
        sys.exit(0)