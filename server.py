from socket import *
import threading
import sqlite3
import json

class Server:

    def __init__(self, port):
        self.BUFFERSIZE = 1024
        self.serverSoc = socket(AF_INET, SOCK_STREAM)
        self.port = port
        self.serverSoc.bind(("172.20.113.190", self.port))
        # self.createTabSSle()

    def createTable(self):
        dbConnection = sqlite3.connect('netProj.db')
        db = dbConnection.cursor()
        q = """
        CREATE TABLE onlines (
        alias VARCHAR(100) PRIMARY KEY UNIQUE, 
        ip VARCHAR(100), 
        status INTEGER,
        mac INTEGER UNIQUE);"""
        db.execute(q)
        dbConnection.commit()
        print('Table created')

    def start(self):
        print("Starting server at port "+str(self.port))
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
            conn.send(self.handleCommand(cmd, opData, mac, addr, db, dbConnection))
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
        dbConnection.commit()
        dbConnection.close()
        conn.close()
        print('Connection Closed')

    def handleCommand(self, cmd, opData, mac, addr, db, dbConnection):
        opData = opData.lstrip()
        opData = opData.rstrip()
        if cmd == 'alias':
            return self.handleALIAS(opData, addr, mac, db, dbConnection)
        elif cmd == 'isonline':
            return self.handleISONLINE(opData, db, dbConnection)

    def handleALIAS(self, opData, addr, mac, db, dbConnection):
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
                db.execute(q, (a, ))
                return 'deleted'.encode()
            else:
                return 'undefined_cmd'.encode()
        else:
            q = """SELECT * FROM onlines WHERE alias=?"""
            db.execute(q, (opData,))

            if len(db.fetchall()) == 0:
                q = """REPLACE INTO onlines (alias, ip, status, mac) VALUES (?, ?, ?, ?)"""
                db.execute(q, (opData, ip, 1, mac))
                dbConnection.commit()
                # conn.send('success'.encode())
                print('success')
                return 'success'.encode()
            else:
                print('no_success'.encode())
                return 'no_success'.encode()

    def handleISONLINE(self, opData, db, dbConnection):
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
                    db.execute(q, (data,))
                    r = db.fetchall()
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
                    db.execute(q, (data,))
                    r = db.fetchall()
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
                db.execute(q)
                r = db.fetchall()
                if len(r) != 0:
                    for row in r:
                        d[row[0]] = (row[1], row[2])
                else:
                    d['no_no_no'] = ('0.0.0.0', '0')
        tosend = json.dumps(d)
        print('Data Sent')
        return tosend.encode()

def create_server(port):
    s = Server(port)
    s.start()

if __name__ == '__main__':
    thread_sam = threading.Thread(target=create_server, args=(6000,))
    thread_reuben = threading.Thread(target=create_server, args=(6001,))

    thread_sam.start()
    thread_reuben.start()

    thread_sam.join()
    thread_reuben.join()