import socket

PORT = 50001
HOSTNAME = socket.gethostname()
IP = socket.gethostbyname(HOSTNAME)

closeConnection = True


def main():
    # 1. Create a socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2. Connect to remote server
    clientSocket.connect((IP, PORT))

    while True:
        close = True
        message = input("Enter a message")

        # 4. Send the message to the server1
        clientSocket.send(message.encode())

        # receive response from server
        ## response = recieveMessage(clientSocket)
        ## print(response)

        if close:
            # 5. Close the socket
            clientSocket.close()
            break


if __name__ == "__main__":
    main()
