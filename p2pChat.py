import socket
import threading
import sys
import re
import os


# Method to generate a list of connected hosts
def scan(host_ip, port):
    # Create empty lists for threads and connections
    threads = []
    con_list = []

    # Extract the first two octets of the IP address
    network_address = re.search(r'\d+.\d+', host_ip).group()

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

    # Wait for all searching threads to complete before continuing
    for thread in threads:
        thread.join()

    print('Scan complete.')
    # Return the complete list of connections to the created Client object
    return con_list


class SendThread(threading.Thread):
    # a thread that will listen for command prompt user input and broadcast to all connected peers
    def __init__(self, client):
        # client    - the client object for this host
        super(SendThread, self).__init__()
        self.client = client

    def run(self):
        # continuously listen for command line input until user quits out of chat
        while True:
            message = input()
            if message == '\\q':
                # user has asked to quit, send leave messages and exit program
                self.client.broadcast(f'{self.client.name} has left the chat.')
                print('Goodbye!')
                os._exit(0)
            else:
                self.client.broadcast(message)
                print(f'\r{self.client.name}: ', end='')


# Every peer is an instance of the Client class, which handles sending and receiving messages to other peers,
# as well as being able to accept connections for new clients joining the chat room
class Client:
    def __init__(self, ip, port, client_name):
        # ip        - the local host IP address
        # port      - the port number the chat room operates on
        # peer_list - a list of connections to the other clients on the chat room
        # name      - the user's chosen username
        self.ip = ip
        self.port = port
        self.peer_list = scan(ip, port)
        self.name = client_name

    # Method to send messages to all the other connected peers
    def broadcast(self, message):
        # if the message is blank, do not broadcast
        if len(message) < 1:
            return
        # Iterate through the list of connections from the peers, and send the message to them in turn
        for peer in self.peer_list:
            try:
                # If the message is a connect or disconnect message, they take a different format
                if message == f'{self.name} has entered the chat.' or message == f'{self.name} has left the chat.':
                    peer.sendall(f'{message}\n'.encode())
                # All other messages take the format 'username: message'
                else:
                    peer.sendall(f'{self.name}: {message}\n'.encode())
            # If the peer is available to accept a message, remove them from the list of connections
            except:
                self.peer_list.remove(peer)

    # The method performs the formalities when first joining the chat room
    # It continues by always listening for new connections
    def start(self):
        # Broadcast the connect message to the other clients and welcomes the user to the chat room
        self.broadcast(f'{self.name} has entered the chat.')
        print(f'Welcome to the chat room! To quit, type \\q.\n{self.name}: ', end='')

        # Create a thread to listen for incoming messages for each peer in the list of connections
        for peer in self.peer_list:
            receiver = ReceiveThread(peer, self.name)
            receiver.start()

        # Create a thread to accept user input and later send the message to the other peers
        send = SendThread(self)
        send.start()

        # Create a TCP socket on the port number to actively listen for new clients joining the chat room
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        sock.listen(1)

        # Listen for new connections indefinitely.
        # When a new client attempts to connect, add them to the list of connections
        while True:
            connection, address = sock.accept()
            self.peer_list.append(connection)
            receiver = ReceiveThread(connection, self.name)
            receiver.start()


class ReceiveThread(threading.Thread):
    def __init__(self, connection, name):
        # connection    - a connection to a peer
        # name          - the name of the user for this host
        super(ReceiveThread, self).__init__()
        self.connection = connection
        self.name = name

    def run(self):
        # as long as connection is alive continuously listen for a message and print if received,
        #   when connection is closed a ConnectionResetError is thrown and we will exit the loop
        while True:
            try:
                message = self.connection.recv(1024).decode()
                print(f'\r{message}{self.name}: ', end='')
            except ConnectionResetError:
                return


# Method to determine the local host IP address that works on both macOS and Windows
# The default function to get the local host IP doesn't work; it returns the loopback address 127.0.0.1 on macOS
def get_host_ip():
    # Create a UDP socket and attempt to connect to 8.8.8.8 (Google's DNS server)
    # It will attempt to connect to the internet network
    # getsockname() will returns the socket's own address, which should be the local host address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def __main__():
    # def port we will use
    port = 42069

    # take user input for name, create client with given name, and start client
    name = input("Enter a name to chat: ")
    client = Client(get_host_ip(), port, name)
    client.start()


if __name__ == "__main__":
    __main__()
