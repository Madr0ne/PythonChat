print('poop')

import socket
import threading
import sys
import time
from random import randint
import re

SOCKET = 50001



def scan(network_address, port):
    threads = []
    con_list = []

    def __do_scan(first_three, start):
        for i in range(start, start + 15):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(0.1)

            if not sock.connect_ex((f'{first_three}.{i}', port)):
                con_list.append(sock)
        return

    for i in range(255):
        for j in range(0, 256, 16):
            t = threading.Thread(target=__do_scan, args=(f'{network_address}.{i}', j))
            threads.append(t)
            t.start()

    for thread in threads:
        thread.join()
    return con_list


class Peer:

    def send_msg(self):
        while True:
            message = self.name + ': ' + input("")
            print(message)
            for connection in self.connections:
                connection.send(bytes(message, 'utf-8'))

    def __init__(self, name, connectionsList):
        print('Connected!')
        self.name = name
        self.connections = connectionsList
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', SOCKET))
        sock.listen(1)

        for connection in self.connections:
            socketThread = threading.Thread(target=self.handler, args=(connection,))
            socketThread.daemon = True
            socketThread.start()

        sendThread = threading.Thread(target=self.send_msg)
        sendThread.daemon = True
        sendThread.start()

        while True:
            connection, a = sock.accept()
            socketThread = threading.Thread(target=self.handler, args=(connection,))
            socketThread.daemon = True
            socketThread.start()
            self.connections.append(connection)
            print(str(a[0]) + ':' + str(a[1]), " connected.")

    def handler(self, c):
        while True:
            data = c.recv(1024)
            print(str(data, 'utf-8'))
            if not data:
                self.connections.remove(c)
                c.close()
                break



print('hi')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
hostIP = str(s.getsockname()[0])
print(hostIP)
networkAddress = re.search('\d+\.\d+', hostIP).group()

name = input("Enter your name:")

print('Finding local hosts, please wait...')
scannedConnections = scan(networkAddress, SOCKET)

peer = Peer(name, scannedConnections)