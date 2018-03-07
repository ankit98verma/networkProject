from socket import *
import threading
import sqlite3
import json

class Server:

    def __init__(self):
        self.BUFFERSIZE = 1024
        self.serverSoc = socket(AF_INET, SOCK_STREAM)
        self.serverSoc.bind(("localhost", 5000))
        self.dbConnection = sqlite3.connect('netProj.db')
        self.db = self.dbConnection.cursor()
        self.createTable()

    def createTable(self):
        q = """
        CREATE TABLE onlines (
        alias VARCHAR(100) PRIMARY KEY UNIQUE, 
        ip VARCHAR(100), 
        status INTEGER,
        mac INTEGER UNIQUE);"""
        self.db.execute(q)
        self.dbConnection.commit()
        print('Table created')

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

        db = self.dbConnection.cursor()
        recData = conn.recv(self.BUFFERSIZE).decode()
        mac = json.loads(recData)
        q = """SELECT * FROM onlines WHERE mac=?"""
        db.execute(q, (mac, ))
        r = db.fetchall()
        if len(r) == 0:
            conn.send("not_reg".encode())
        else:
            d = r[0]
            d = json.dumps(d[3])
            conn.send(d.encode())

        while True:
            recData = conn.recv(self.BUFFERSIZE)
            recData = recData.lstrip()
            recData = recData.rstrip()
            if len(recData) == 0:
                break

            recData = recData.decode()

            cmd = recData[:recData.index(' ')]
            opData = recData[recData.index(' ')+1:]
            conn.send(self.handleCommand(cmd, opData, mac, addr))
        print('Closing Connection')
        q = """SELECT * FROM onlines WHERE ip=?"""
        db.execute(q, (addr[0], ))
        r = db.fetchall()
        if len(r) == 0:
            print('Not registered in database')
        else:
            q = """UPDATE onlines SET status=? WHERE ip=?"""
            db.execute(q, (0, addr[0],))
            print("Setting status to 0")
        self.dbConnection.commit()
        self.dbConnection.close()
        conn.close()
        print('Connection Closed')

    def handleCommand(self, cmd, opData, mac, addr):
        opData = opData.lstrip()
        opData = opData.rstrip()
        if cmd == 'alias':
            return self.handleALIAS(opData, addr, mac)
        elif cmd == 'isonline':
            return self.handleISONLINE(opData)

    def handleALIAS(self, opData, addr, mac):
        ip = addr[0]

        try:
            index = opData.index(' ')
        except:
            index = -1
        if index > 0:
            option = opData[:opData.index(' ')]
            if option == '-rm':
                a = opData[opData.index(' ')+1:]
                q = """DELETE FROM onlines WHERE alias = ?"""
                self.db.execute(q, (a, ))
                return 'deleted'.encode()
            else:
                return 'undefined_cmd'.encode()
        else:
            q = """SELECT * FROM onlines WHERE alias=?"""
            self.db.execute(q, (opData,))

            if len(self.db.fetchall()) == 0:
                q = """REPLACE INTO onlines (alias, ip, status, mac) VALUES (?, ?, ?, ?)"""
                self.db.execute(q, (opData, ip, 1, mac))
                self.dbConnection.commit()
                # conn.send('success'.encode())
                print('success')
                return 'success'.encode()
            else:
                print('no_success'.encode())
                return 'no_success'.encode()

    def handleISONLINE(self, opData):
        d = dict()
        try:
            index = opData.index(' ')
        except:
            index = -1
        if index > 0:
            option = opData[:opData.index(' ')]
            while True:
                try:
                    index = opData.index(' ')
                    opData = opData[index + 1:]
                except:
                    break
                try:
                    nextIndex = opData.index(' ')
                except:
                    nextIndex = len(opData)
                data = opData[:nextIndex]
                if option == '-a':
                    q = """SELECT * FROM onlines WHERE alias=?"""
                    self.db.execute(q, (data,))
                    r = self.db.fetchall()
                    if len(r) > 0:
                        row = r[0]
                        if len(r) == 0:
                            d[data] = ('0.0.0.0', '0')
                        else:
                            d[row[0]] = (row[1], row[2])
                    if nextIndex == len(opData):
                        break
                elif option == '-ip':
                    q = """SELECT * FROM onlines WHERE ip=?"""
                    self.db.execute(q, (data,))
                    r = self.db.fetchall()
                    if len(r) > 0:
                        row = r[0]
                        if len(r) == 0:
                            d[data] = ('0.0.0.0', '0')
                        else:
                            for row in r:
                                d[row[0]] = (row[1], row[2])
                    if nextIndex == len(opData):
                        break
        else:
            if opData == '-all':
                q = """SELECT * FROM onlines"""
                self.db.execute(q)
                r = self.db.fetchall()
                if len(r) != 0:
                    for row in r:
                        d[row[0]] = (row[1], row[2])
                else:
                    d['no_no_no'] = ('0.0.0.0', '0')
        tosend = json.dumps(d)
        print('Data Sent')
        return tosend.encode()

if __name__ == '__main__':
    s = Server()
    s.start()
