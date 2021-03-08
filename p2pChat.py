import socket as sock
import threading


class Server:
    connections = []

    def __init__(self):
        s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = str(s.getsockname()[0])
        s.close()
        s = sock.socket(sock.AF_INET, sock .SOCK_STREAM)
        s.bind((IP, 50001))
        #s.bind(('10.200.1.5', 50001))
        s.listen(1)
        s.close()


if __name__ == "__main__":
    Server()
