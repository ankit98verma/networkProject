from socket import *
import threading
import sqlite3


class Server:

    def __init__(self):
        # self.createTable()
        self.BUFFERSIZE = 1024
        self.serverSoc = socket(AF_INET, SOCK_STREAM)
        self.serverSoc.bind(("localhost", 5000))

    def createTable(self):
        dbConnection = sqlite3.connect('netProj.db')
        db = dbConnection.cursor()
        q = """
        CREATE TABLE onlines (
        alias VARCHAR(100) PRIMARY KEY UNIQUE, 
        ip VARCHAR(100), 
        status INTEGER );"""
        db.execute(q)
        dbConnection.commit()
        print('Table created')
        dbConnection.close()

    def start(self):
        print("Starting server at port 5000")
        while True:
            self.serverSoc.listen(10)

            connection, address = self.serverSoc.accept()
            print("Connected to ", address)

            client_thread = threading.Thread(target=self.clientHandle, args=(connection, address,))

            client_thread.start()

            print('Joining Thread')
            client_thread.join()

    def clientHandle(self, conn, addr):
        dbConnection = sqlite3.connect('netProj.db')
        db = dbConnection.cursor()
        while True:
            recData = conn.recv(self.BUFFERSIZE)
            if len(recData) == 0:
                break

            recData = recData.decode()

            cmd = recData[:recData.index(' ')]
            opData = recData[recData.index(' '):]
            if cmd == 'alias':
                a = opData
                ip = addr[0]
                while True:
                    q = """SELECT * FROM onlines WHERE alias=?"""
                    db.execute(q, (a,))

                    if len(db.fetchall()) == 0:
                        q = """INSERT INTO onlines (alias, ip, status) VALUES (?, ?, ?)"""
                        db.execute(q, (a, ip, 1))
                        dbConnection.commit()
                        conn.send('success'.encode())
                        print('success')
                        break
                    else:
                        print('no_success'.encode())
                        conn.send('no_success'.encode())
        q = """ """
        dbConnection.close()
        conn.close()



if __name__ == '__main__':
    s = Server()
    s.start()
