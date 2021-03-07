import socket
import threading


class SendMessages(threading.Thread):
    # TODO Thread to listen for keyboard input on terminal and then send message to all connected clients. exit if message == 'QUIT' or something
    def __init__(self, peerList, name):
        super(SendMessages, self).__init__()
        self.peerList = peerList
        self.name = name

    def run(self):
        return


class ReceiveMessages(threading.Thread):
    # TODO Each time a connection is received a new instance of this thread will be created to receive messages form that connection and print to terminal
    def __init__(self):
        super(ReceiveMessages, self).__init__()

    def run(self):
        return


class Client:
    def __init__(self, host, port):
        super(Client, self).__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peerList = []
        self.name = None


    def scanForClients(self):
        # TODO scans subnet for other hosts running, makes connections, and adds them to peer list
        return

    def start(self):
        # TODO call the scan, bind socket, start listening for connections, all that
        return

    def removePeer(self, con):
        self.peerList.remove(con)

def main():
    host = socket.gethostbyname(socket.gethostname())
    port = 50001
    client = Client(host, port)
    client.start()

if __name__ == '__main__':
    main()
