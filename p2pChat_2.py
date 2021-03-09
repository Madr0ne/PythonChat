import socket
import threading
import sys
import re
import os

def scan(host_ip, port, host_name):
    threads = []
    con_list = []
    network_address = re.search('\d+\.\d+', host_ip).group()

    def __do_scan(first_three, start):
        for k in range(start, start + 7):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(0.05)
            
            if f'{first_three}.{k}' == host_ip:
                continue
            
            if not sock.connect_ex((f'{first_three}.{k}', port)):
                sock.settimeout(None)
                sock.sendall(f'{host_name} has joined the chat'.encode())
                con_list.append(sock)
        return

    print('Beginning network scan...')
    for i in range(255):
        for j in range(0, 256, 8):
            t = threading.Thread(target=__do_scan, args=(f'{network_address}.{i}', j))
            try:
                t.start()
            except RuntimeError:
                j -= 8
                continue
            threads.append(t)
    for thread in threads:
        thread.join()
    print('Scan complete.')
    return con_list


class SendThread(threading.Thread):
    def __init__(self, client):
        super(SendThread, self).__init__()
        self.client = client

    def run(self):
        while True:
            message = input()
            if message == '\\q':
                print('Goodbye!')
                os._exit(0)
            else:
                self.client.broadcast(message)
                print(f'\r{self.client.name}: ', end='')


def listen_for_peers(client):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((client.ip, client.port))
    sock.listen(1)

    while True:
        connection, address = sock.accept()
        if address[0] != client.ip:
            client.peer_list.append(connection)
            receiver = ReceiveThread(connection, client.name)
            receiver.start()


class Client:
    def __init__(self, ip, port, client_name):
        self.ip = ip
        self.port = port
        self.peer_list = []
        self.name = client_name

    def broadcast(self, message):
        for peer in self.peer_list:
            if not peer.send(f'{self.name}: {message}'.encode()):
                print('Exception raised! No message sent.')
                self.peer_list.remove(peer)

    def start(self):
        for peer in self.peer_list:
            receiver = ReceiveThread(peer, self.name)
            receiver.start()

        send = SendThread(self)
        send.start()

        T = threading.Thread(target=listen_for_peers, args=(self,))
        T.start()

        self.peer_list += scan(self.ip, self.port, self.name)
        print(f'Welcome to the chat room! To quit, type \\q.\n{self.name}: ', end='')
        T.join()


class ReceiveThread(threading.Thread):
    def __init__(self, connection, name):
        super(ReceiveThread, self).__init__()
        self.connection = connection
        self.name = name

    def run(self):
        while True:
            try:
                message = self.connection.recv(1024).decode()
                print(f'\r{message}\n{self.name}: ', end='')
            except ConnectionResetError:
                return


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def __main__():
    port = 50001

    name = input("Enter a name to chat: ")
    try:
        client = Client(get_host_ip(), port, name)
        client.start()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    __main__()