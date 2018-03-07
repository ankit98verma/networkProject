from socket import *
from uuid import getnode as get_mac
import threading
import json
import os

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

    @property
    def server_ip(self):
        return self._server_ip

    @property
    def reception_port(self):
        return self._reception_port

    @property
    def transmission_port(self):
        return self._transmission_port

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
            self._server_ip = '172.20.113.43'
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
        query = dict( )
        query['command'] = command
        # query['arguemets'] = arguements
        json_q = json.dumps(query)
        sock.send(json_q.encode())

        received_json = sock.recv(self.BUFFERSIZE)
        received_dict = json.loads(received_json)

        if received_dict['return'] is 'success':
            for entry in received_dict['data']:
                print('$$ %s'%str(entry))
        else:
            print('$$ Query Failed! Try again\n')

    def reception(self, sock):
        """
        The function handling reception
        :param sock: The socket which communicates and looks for reception
        :return:
        """
        response = 'N'
        while response not in ['Y', 'y']:
            sock.listen(1)
            connection, address = sock.accept()
            print('$$ A connection has been successfully established to yur node from %s\n'%address)

            request = (sock.recv(self.BUFFERSIZE)).decode()
            if request.split(':')[0] is 'fetch':
                file_path = request.split(':')[1]
                permission = input('$$ %s has requested %s from you. Y/N : '%(address, file_path))
                if permission in ['Y', 'y']:
                    if os.path.isfile(file_path):
                        sock.send('yes'.encode())
                        with open(file_path,'r') as f:
                            for l in f.read():
                                sock.send(l.encode())
                        f.close()
                    elif os.path.isfile(os.path.join(os.path.expanduser('~/Documents'),file_path)):
                        file_path = os.path.join(os.path.expanduser('~/Documents'),file_path)
                        sock.send('yes'.encode())
                        with open(file_path,'r') as f:
                            for l in f.read():
                                sock.send(l.encode())
                        f.close()
                        sock.send('ENDOFFILE'.encode())
                    else:
                        print('$$ File not Found on your machine\n')
                        sock.send('NF'.encode())
                else:
                    sock.send('DENIED'.encode())

            response = input('$$ File successfully sent. Do you wish to end reception (Y|N) : ')
            if response in ['Y', 'y']:
                print('$$ Tearing Down the socket\n')
                # TODO : Disconnect the socket Ankit! Such that it will be reusable



    def getf(self, sock, ip_alias, file_name, PORT=5000):
        """
        The function which gets a file from the other clients
        :param transmit_socket: The socket on which it has to communicate
        :param ip_alias: The alias or ip on which to connect
        :param file_name: the file to fetch
        :return:
        """
        sock.connect((ip_alias, PORT))
        sock.send(('fetch:%s'%file_name).encode())
        reply = (sock.recv(self.BUFFERSIZE)).decode()
        if reply is 'yes':
            with open(file_name, 'wb') as f:
                l = (sock.recv(self.BUFFERSIZE)).decode()
                while l is not 'ENDOFFILE':
                    f.write(l)
                    l = (sock.recv(self.BUFFERSIZE)).decode()
            f.close()
        elif reply is 'DENIED':
            print('$$ Permission Denied\n')
        elif reply is 'NF':
            print('$$ File Not Found\n')
        else:
            print('$$ Unknown Response from Client\n')
        # TODO : Free the socket, i.e. disconnect it So it can be reused

    def console(self, main_server_socket, transmit_sock):
        """
        The function which runs the console on the client machine
        :return:
        """
        while True:
            inp = input('$$ ')

            if inp is 'exit':
                print('$$ Now initiating END\n')
                break
            elif inp.split(' ')[0] is 'isonline':
                if inp.split(' ')[1] is '-p':
                    print('$$ Fetching status of %s \n'%inp.split(' ')[2])
                    self.server_query(main_server_socket, inp)
                elif inp.split(' ')[1] is '-A':
                    print('$$ Fetching list of all Online\n')
                    self.server_query(main_server_socket, inp)
                elif inp.split(' ')[1] is '-a':
                    print('$$ Fetching status of %s \n'%inp.split(' ')[2])
                    self.server_query(main_server_socket, inp)
                else:
                    print('$$ Acceptable arguements with isonline are -p -a -A\n')
            elif inp.split(' ')[0] is 'getf':
                ip_alias = inp.split(' ')[1]
                file_name = inp.split(' ')[2]
                PORT = int(input('$$ Enter the port you will communicate on\n'))
                self.getf(transmit_sock, ip_alias, file_name, PORT)
            else:
                print('$$ Invalid command! Try again\n')


    def run_time(self):
        """
        A function depicting the runtime of the Client as a whole
        :return: void
        """
        # Code for setting up a connection on server
        main_server_socket = socket(AF_INET, SOCK_STREAM)
        main_server_socket.connect((self.server_ip, self.server_port))
        main_server_socket.send(('mac_id:%s'%str(self.mac_id)).encode())
        mac_id_reply = (main_server_socket.recv(self.BUFFERSIZE)).decode()
        mac_id_reply_key = mac_id_reply.split(' ')[0]
        mac_id_reply_rem = mac_id_reply.split(' ')[1:]
        if mac_id_reply_key is 'OK':
            print('Welcone back, you have retained your old ID %s\n'%mac_id_reply_rem[0])
        else:
            while True:
                self.alias = input('Pleas type in your new Alias: ')
                main_server_socket.send(('alias %s'%self.alias).encode())
                alias_reply = (main_server_socket.recv(self.BUFFERSIZE)).decode()
                if alias_reply is'success':
                    print('The alias name is successfully set to %s\n'%self.alias)
                    break

        # Setting up transmit and receive sockets
        transmit_socket = socket(AF_INET, SOCK_STREAM)
        receive_socket = socket(AF_INET, SOCK_STREAM)

        # Run a thread that looks for incoming connections and processes the commands that comes
        receive_thread = threading.Thread(target= self.reception, args=(receive_socket, transmit_socket,))
        receive_thread.start()

        # Running a Console on another thread
        console_thread = threading.Thread(target=self.console, args=(main_server_socket, transmit_socket,))
        console_thread.start()

        receive_thread.join()
        console_thread.join()