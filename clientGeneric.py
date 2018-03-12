from socket import *
from uuid import getnode as get_mac
import threading
import json
import os
from tkinter import filedialog
from tkinter import *

class GenericClient:
    """
    Generic class code for the client end, which establishes communication with the server, and
    then co-ordinates activities among other clients in order to transfer and receive files.
    """
    def __init__(self, alias, serverIP='none', serverPort='none', transmissionPort='none', receptionPort='none'):
        """
        The constructor of the generic class which at the moment takes only the alias name on
        creation and sets it efficiently as a class property
        :param alias: the alias name by which you are recognized online on the server
        """
        self.alias = alias
        self.BUFFERSIZE = 1024
        self.server_ip = serverIP
        self.server_port = serverPort
        self.transmission_port = transmissionPort
        self.reception_port = receptionPort
        self.mac_id = get_mac()
        self.isrunning = True

    @property
    def server_ip(self):
        return self._server_ip

    @property
    def isrunning(self):
        return self._isRunning

    @property
    def reception_port(self):
        return self._reception_port

    @property
    def transmission_port(self):
        return self._transmission_port

    @isrunning.setter
    def isrunning(self, x):
        if type(x) is bool:
            self._isRunning = x
        else:
            self._isRunning = True


    @transmission_port.setter
    def transmission_port(self, x):
        if x is 'none':
            self._transmission_port = 5000
        else:
            self._transmission_port =  x

    @reception_port.setter
    def reception_port(self, x):
        if x is 'none':
            self._reception_port = 5000
        else:
            self._reception_port =  x

    @server_ip.setter
    def server_ip(self, x):
        if x is 'none':
            self._server_ip = 'localhost'
        else:
            self._server_ip = x

    @property
    def server_port(self):
        return self._server_port

    @server_port.setter
    def server_port(self, x):
        if x is 'none':
            self._server_port = '5000'
        else:
            self._server_port = x

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, x):
        if x not in ['', ' ']:
            self._alias = x
        else:
            self._alias = 'default'


    def server_query(self, sock, command):
        """
        The function which queries the server and gets the reply and prints it
        :param sock: The socket on which to query
        :param command: The command queried
        :param arguements: The arguements user entered
        :return:
        """
        # query = dict( )
        # query['command'] = command
        # query['arguemets'] = arguements
        # json_q = json.dumps(query)
        sock.send(command.encode())

        received_json = (sock.recv(self.BUFFERSIZE)).decode()
        # received_dict = json.loads(received_json)
        print(received_json)
        # if received_dict['return'] is 'success':
        #     for entry in received_dict['data']:
        #         print('$$ %s'%str(entry))
        # else:
        #     print('$$ Query Failed! Try again\n')
        # for key in received_dict:
        #     print(key+' - '+received_dict[key])

    # def reception(self, sock):
    #     """
    #     The function handling reception
    #     :param sock: The socket which communicates and looks for reception
    #     :return:
    #     """
    #     flag = 'first'
    #     while True:
    #         # ip = input('Type your current IP: ')
    #         if flag == 'first':
    #             receive_port = int(input('What port you wanna receive on: '))
    #             sock.bind(('172.20.113.190', receive_port))
    #             print('$$ IP bound successfully\n')
    #             flag = 'second'
    #         sock.listen(1)
    #         print('$$ Started Listening\n')
    #         connection, address = sock.accept()
    #         print('$$ A connection has been successfully established to yur node from '+str(address)+'\n')
    #         request = (connection.recv(self.BUFFERSIZE)).decode()
    #         if request.split(':')[0] == 'fetch':
    #             file_path = request.split(':')[1]
    #             permission = input('$$ %s has requested %s from you. Y/N : '%(address, file_path))
    #             if permission in ['Y', 'y']:
    #                 if os.path.isfile(file_path):
    #                     connection.send('yes'.encode())
    #                     with open(file_path,'r') as f:
    #                         for l in f.read():
    #                             connection.send(l.encode())
    #                     f.close()
    #                 elif os.path.isfile(os.path.join(os.path.expanduser('~/Documents'),file_path)):
    #                     file_path = os.path.join(os.path.expanduser('~/Documents'),file_path)
    #                     connection.send('yes'.encode())
    #                     with open(file_path,'r') as f:
    #                         for l in f.read():
    #                             connection.send(l.encode())
    #                     f.close()
    #                     connection.send('ENDOFFILE'.encode())
    #                 else:
    #                     print('$$ File not Found on your machine\n')
    #                     connection.send('NF'.encode())
    #             else:
    #                 connection.send('DENIED'.encode())
    #         else:
    #             connection.send('UC'.encode())
    #
    #         response = input('$$ File successfully sent. Do you wish to end reception (Y|N) : ')
    #         connection.close()
    #         if response in ['Y', 'y']:
    #             print('$$ Tearing Down the socket\n')
    #             break
    #             # sock.close()
    #             #

    def reception(self, sock):
        """
        The function handling reception
        :param sock: The socket which communicates and looks for reception
        :return:
        """
        while self.isrunning:
            try:
                # sock.settimeout(30)
                sock.listen(1)
                print('$$ Started Listening\n')
                connection, address = sock.accept()
            except socket.timeout:
                pass
            except:
                raise
            else:
                print('$$ A connection has been successfully established to yur node from '+str(address)+'\n')
                request = (connection.recv(self.BUFFERSIZE)).decode()
                if request.split(':')[0] == 'fetch':
                    file_path = request.split(':')[1]
                    permission = input('$$ %s has requested %s from you. Y/N : '%(address, file_path))
                    if permission in ['Y', 'y']:
                        root = Tk()
                        root.filename = filedialog.askopenfilename(initialdir=os.path.expanduser('~/'), title='Select file')
                        file_path = root.filename
                        root.destroy()
                        if os.path.isfile(file_path):
                            connection.send(('yes:'+str(os.path.getsize(file_path))).encode())
                            file_size = os.path.getsize(file_path)
                            with open(file_path,'rb') as f:
                                bytes_to_send = f.read(self.BUFFERSIZE)
                                connection.send(bytes_to_send)
                                bytes_sent = len(bytes_to_send)
                                while bytes_sent<file_size:
                                    bytes_to_send = f.read(self.BUFFERSIZE)
                                    connection.send(bytes_to_send)
                                    bytes_sent += len(bytes_to_send)
                            f.close()
                        else:
                            print('$$ File not Found on your machine\n')
                            connection.send('NF'.encode())
                    else:
                        connection.send('DENIED'.encode())
                else:
                    connection.send('UC'.encode())



    def getf(self, sock, ip_alias, file_name, PORT=5000):
        """
        The function which gets a file from the other clients
        :param transmit_socket: The socket on which it has to communicate
        :param ip_alias: The alias or ip on which to connect
        :param file_name: the file to fetch
        :return:
        """
        print('$$ Now connecting to IP : %s on Port : %s\n'%(ip_alias,PORT))
        sock.connect((ip_alias, PORT))
        print('$$ Connected\n')
        sock.send(('fetch:%s'%file_name).encode())
        print('$$ Requesting file\n')
        reply = (sock.recv(self.BUFFERSIZE)).decode()
        reply = reply.split(':')
        if reply[0] == 'yes':
            file_size = int(reply[1])
            print('Receiving FILE of Size '+str(file_size)+'\n')
            root1 = Tk()
            root1.filename = filedialog.asksaveasfilename(initialdir=os.path.expanduser('~/'), title='Save file')
            file_path = root1.filename
            root1.destroy()
            with open(file_path, 'wb') as f:
                data = sock.recv(self.BUFFERSIZE)
                total_received = len(data)
                f.write(data)
                while total_received<file_size:
                    data = sock.recv(self.BUFFERSIZE)
                    total_received += len(data)
                    f.write(data)
                    print("{0:.2f}".format((total_received/float(file_size))*100)+" % downloaded\n")
                print("Download Complete\n")
            f.close()
        elif reply == 'DENIED':
            print('$$ Permission Denied\n')
        elif reply == 'NF':
            print('$$ File Not Found\n')
        else:
            print('$$ Unknown Response from Client\n')
        # Free the socket, i.e. disconnect it So it can be reused
        sock.close()

    def console(self, main_server_socket):
        """
        The function which runs the console on the client machine
        :return:
        """
        while True:
            inp = input('$$ ')
            if inp == 'exit':
                print('$$ Now initiating END\n')
                print('$$ 30 seconds to END\n')
                self.isrunning = False
                break
            elif inp.split(' ')[0] == 'isonline':
                if inp.split(' ')[1] == '-p':
                    print('$$ Fetching status of %s \n'%inp.split(' ')[2])
                    self.server_query(main_server_socket, inp)
                elif inp.split(' ')[1] == '-all':
                    print('$$ Fetching list of all Online\n')
                    self.server_query(main_server_socket, inp)
                elif inp.split(' ')[1] == '-a':
                    print('$$ Fetching status of %s \n'%inp.split(' ')[2])
                    self.server_query(main_server_socket, inp)
                else:
                    print('$$ Acceptable arguements with isonline are -p -a -all\n')
            elif inp.split(' ')[0] == 'getf':
                if len(inp.split(' ')) is 3:
                    ip_alias = inp.split(' ')[1]
                    file_name = inp.split(' ')[2]
                    PORT = int(input('$$ Enter the port you wish to communicate with on the remote machine\n'))
                    self.getf(socket(AF_INET, SOCK_STREAM), ip_alias, file_name, PORT)
            else:
                print('$$ Invalid command! Try again\n')

    def welcome(self):
        """
        Standard welcome function
        :return: void
        """
        print("************************************************************\n")
        print("                          Welcome                           \n")
        print("                            to                              \n")
        print("                          Jaggery                           \n")
        print("____________________________________________________________\n")
        print("           Developers - Ankit Verma, Samvram Sahu           \n")
        print("************************************************************\n")

    def aftermath(self):
        """
        THe ending
        :return:
        """
        print("************************************************************\n")
        print("                        Thank You                           \n")
        print("                           for                              \n")
        print("                      using Jaggery                         \n")
        print("____________________________________________________________\n")
        print("           Bugs - +919497300461 - Samvram Sahu              \n")
        print("************************************************************\n")

    def run_time(self):
        """
        A function depicting the runtime of the Client as a whole
        :return: void
        """
        # Code for setting up a connection on server
        self.welcome()
        main_server_socket = socket(AF_INET, SOCK_STREAM)
        main_server_socket.connect((self.server_ip, self.server_port))
        main_server_socket.send((json.dumps(self.mac_id)).encode())
        mac_id_reply = (main_server_socket.recv(self.BUFFERSIZE)).decode()
        if mac_id_reply == 'not_reg':
            while True:
                self.alias = input('Pleas type in your new Alias: ')
                main_server_socket.send(('alias %s'%(self.alias)).encode())
                alias_reply = (main_server_socket.recv(self.BUFFERSIZE)).decode()
                if alias_reply == 'success':
                    print('The alias name is successfully set to %s\n'%self.alias)
                    break
        else:
            print('Welcone back, you have retained your old ID %s\n' % mac_id_reply)

        # Setting up transmit and receive sockets
        # transmit_socket = socket(AF_INET, SOCK_STREAM)
        receive_socket = socket(AF_INET, SOCK_STREAM)
        receive_ip = input('$$ Type your current IP you want reception on: ')
        receive_port = int(input('$$ What port you wanna receive on: '))
        receive_socket.bind((receive_ip, receive_port))
        print('$$ IP bound successfully\n')

        # Run a thread that looks for incoming connections and processes the commands that comes
        self.isrunning = True
        receive_thread = threading.Thread(target= self.reception, args=(receive_socket,))
        receive_thread.start()

        # Running a Console on another thread
        console_thread = threading.Thread(target=self.console, args=(main_server_socket, ))
        console_thread.start()

        receive_thread.join()
        console_thread.join()

        # transmit_socket.close()
        receive_socket.close()
        self.aftermath()