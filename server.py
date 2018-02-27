from socket import *
import threading
import sqlite3

BUFFERSIZE = 1024


def rec_tcp(conn):
    data = conn.recv(BUFFERSIZE)
    print(data.decode())
    data = conn.recv(BUFFERSIZE)
    print(data.decode())



def start():
    serverSoc = socket(AF_INET, SOCK_STREAM)

    serverSoc.bind(("172.20.10.39", 5000))

    print("Starting server at port 5000")
    while True:
        serverSoc.listen(10)

        connection, address = serverSoc.accept()
        print("Connected to ", address)

        rec_thread = threading.Thread(target=rec_tcp, args=(connection,))

        rec_thread.start()

        print('Joining Thread')
        rec_thread.join()

    print("Closing Server")

if __name__ == '__main__':
    start()
