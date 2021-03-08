import socket
import threading
import time
import re

def scan(networkAddress, port):
    threads = []
    conList = []
    def __doScan(firstThree, start):
        for i in range(start, start + 7):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(0.25)

            if not sock.connect_ex((f'{firstThree}.{i}', port)):
                conList.append(sock)
        return

    for i in range(255):
        for j in range(0, 256, 8):
            t = threading.Thread(target = __doScan, args = (f'{networkAddress}.{i}', j))
            threads.append(t)
            t.start()

    for thread in threads:
        thread.join()
    return conList

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
hostIP = s.getsockname()[0]
s.close()
    
networkAddress = re.search('\d+\.\d+', hostIP).group()
port = 50001

start = time.time()
cons = scan(networkAddress, port)

print(cons)
print(time.time() - start)