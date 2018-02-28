from socket import *
import threading
import sqlite3


BUFFERSIZE = 1024


def rec_tcp(conn, addr):

    data  = -1
    while data != 0:
        data = conn.recv(BUFFERSIZE)
        alias = data.decode()


        print(alias)
        ip = addr[0]
        print(ip)
    print('Connection Closed')

def processCommands(s):
    sInd = s.index(' ')
    comm = s[:sInd]



def start():
    serverSoc = socket(AF_INET, SOCK_STREAM)

    serverSoc.bind(("localhost", 5000))

    print("Starting server at port 5000")
    while True:
        serverSoc.listen(10)

        connection, address = serverSoc.accept()
        print("Connected to ", address)

        clientThread = threading.Thread(target=rec_tcp, args=(connection, address,))

        clientThread.start()

        print('Joining Thread')
        clientThread.join()


    print("Closing Server")

if __name__ == '__main__':
    start()
