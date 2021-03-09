import socket
import threading
import sys
import re


def scan(host_ip, port, host_name):
    threads = []
    con_list = []
    network_address = re.search('\d+\.\d+', host_ip).group()

    def __do_scan(first_three, start):
        for k in range(start, start + 15):
            if f'{first_three}.{k}' == host_ip:
                continue
            elif f'{first_three}.{k}' == '10.200.1.122':
                continue

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(0.05)

            if not sock.connect_ex((f'{first_three}.{k}', port)):
                sock.settimeout(None)
                sock.sendall(f'{host_name} has joined the chat'.encode())
                con_list.append(sock)
        return

    print('beginning scan')
    for i in range(255):
        for j in range(0, 256, 16):
            t = threading.Thread(target=__do_scan, args=(f'{network_address}.{i}', j))
            threads.append(t)
            t.start()
    for thread in threads:
        thread.join()
    print('scan complete')
    return con_list


class SendThread(threading.Thread):
    def __init__(self, client):
        super(SendThread, self).__init__()
        self.client = client

    def run(self):
        while True:
            message = input(f'{self.client.name}: ')
            self.client.broadcast(message)


class Client:
    def __init__(self, ip, port, client_name):
        self.ip = ip
        self.port = port
        self.peer_list = scan(ip, port, client_name)
        self.name = client_name

    def broadcast(self, message):
        for peer in self.peer_list:
            peer.sendall(f'{self.name}: {message}'.encode())

    def start(self):
        for peer in self.peer_list:
            receiver = ReceiveThread(peer, self.name)
            receiver.start()

        send = SendThread(self)
        send.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((self.ip, self.port))
        sock.listen(1)

        while True:
            connection, address = sock.accept()
            self.peer_list.append(connection)
            receiver = ReceiveThread(connection, self.name)
            receiver.start()


class ReceiveThread(threading.Thread):
    def __init__(self, connection, name):
        super(ReceiveThread, self).__init__()
        self.connection = connection
        self.name = name

    def run(self):
        while True:
            try:
                message = self.connection.recv(1024).decode()
                if len(message) < 1:
                    return
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

    name = input("Enter name: ")
    try:
        client = Client(get_host_ip(), port, name)
        client.start()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    __main__()