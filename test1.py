from socket import *



BufferSIZE = 1024

if __name__ == '__main__':
    print('Trying to connect to: 172.20.10.39 on port: 5000')

    soc = socket(AF_INET, SOCK_STREAM)
    
    soc.connect(("172.20.10.39", 5000))

    alias = "avatar"
    ip =  "172.20.113.58"

    soc.send(alias.encode())
    soc.send(ip.encode())

    # for i in range(1, 10):
    #     message = "Hello"
    #     soc.send(message.encode())
    #
    #     k = soc.recv(BufferSIZE)
    #     print(k)



