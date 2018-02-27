from socket import *



BufferSIZE = 1024

if __name__ == '__main__':
    print('Trying to connect to: 172.20.10.39 on port: 5000')

    soc = socket(AF_INET, SOCK_STREAM)
    
    soc.connect(("172.20.10.39", 5000))

    message = "Hello"
    soc.send(message.encode())

    k = soc.recv(BufferSIZE)
    print(k)

