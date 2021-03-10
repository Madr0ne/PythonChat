import socket
import threading
import sys
import re
import os

# Method to generate a list of connected hosts
def scan(host_ip, port, host_name):
    # Create empty lists for threads and connections
    threads = []
    con_list = []
    
    # Extract the first two bytes of the IP address
    network_address = re.search('\d+\.\d+', host_ip).group()

    def __do_scan(first_three, start):
        # Loop through each of the 16 IP addresses
        for k in range(start, start + 15):
            # If the generated address matches the host address,
            #   don't bother to try and connect to it
            if f'{first_three}.{k}' == host_ip:
                continue
            
            # Create a TCP socket with an automatic timeout and allow it to reuse 
            #  a local socket in the TIME_WAIT state instead of timing out
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(0.05)
            
            # If no error is raised (connect_ex returns 0), remove
            #   the timeout and add the socket to the connections list
            if not sock.connect_ex((f'{first_three}.{k}', port)):
                sock.settimeout(None)
                con_list.append(sock)
        return

    print('Beginning network scan...')
    
    # Loop through numbers from 0 to 254 for the third byte
    # NOTE: 255 in this spot is reserved for broadcast addresses
    for i in range(255):
        # Start at 0, and move by increments of 16 until 240
        #   to get ranges of 0-15, 16-31, etc. for the fourth byte
        for j in range(0, 256, 16):
            # For each range, start a new thread that calls __do_scan
            
            # Pass the first three bytes (as a formatted string)
            #   and the start of each 16-address range to __do_scan
            t = threading.Thread(target=__do_scan, args=(f'{network_address}.{i}', j))
            # Append each thread to the list created earlier
            threads.append(t)
            t.start()
    
    for thread in threads:
        # After __do_scan has finished, join each thread to the main thread
        thread.join()
    
    print('Scan complete.')
    # Return the complete list of connections to the created Client object
    return con_list


class SendThread(threading.Thread):
    def __init__(self, client):
        super(SendThread, self).__init__()
        self.client = client

    def run(self):
        while True:
            message = input()
            if message == '\\q':
                self.client.broadcast(f'{self.client.name} has left the chat.')
                print('Goodbye!')
                os._exit(0)
            else:
                self.client.broadcast(message)
                print(f'\r{self.client.name}: ', end='')


class Client:
    def __init__(self, ip, port, client_name):
        self.ip = ip
        self.port = port
        self.peer_list = scan(ip, port, client_name)
        self.name = client_name

    def broadcast(self, message):
        for peer in self.peer_list:
            try:
                if message == f'{self.name} has entered the chat.' or message == f'{self.name} has left the chat.':
                    peer.sendall(f'{message}\n'.encode())
                else:
                    peer.sendall(f'{self.name}: {message}\n'.encode())
            except:
                self.peer_list.remove(peer)

    def start(self):
        self.broadcast(f'{self.name} has entered the chat.')
        print(f'Welcome to the chat room! To quit, type \\q.\n{self.name}: ', end='')
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
                print(f'\r{message}{self.name}: ', end='')
            except ConnectionResetError:
                return


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def __main__():
    port = 42069

    name = input("Enter a name to chat: ")
    try:
        client = Client(get_host_ip(), port, name)
        client.start()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    __main__()