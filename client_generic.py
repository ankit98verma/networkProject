from socket import *
import os

class generic_client():
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

    def is_alias_unique(self):
        """
        The function sends a generic command to the server to check if the alias name is set unique
        or not
        :return: true if ID is unique, false if not
        """
        self.server_socket.send(("alias : %s"%self.alias).encode())
        reply = self.server_socket.recv(self.BUFFERSIZE)
        if reply is 'success':
            print('Successfully set alias name to %s\n'%self.alias)
            return False
        else:
            print('Alias name already exists! Try other alias\n')
            return True

    def server_set(self):
        """
        Creates a socket for connection with the server!
        Creates an alias name and stores on database of the server!
        :return: void
        """
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        server_address = (self.server_ip, self.server_port)
        self.server_socket.connect(server_address)

        self.alias = input('Enter the alias name: ')

        while(self.is_alias_unique( )):
            self.alias = input('Enter the alias name: ')

    def login(self):
        """
        The function which is actually available for call by the object
        :return:
        """
        self.server_set()

    def client_send_socket(self, ip):
        """
        A generic function that creates and returns a socket for TCP comm with a given IP
        :param ip: The IP to which the file has to be sent
        :return: socket for the present client to send to a particular IP(connected socket)
        """
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((ip, self.transmission_port))
        return client_socket

    def tear_socket(self, sock):
        """
        Function to tear a socket down formally
        :param sock: The socket to be torn down
        :return: void
        """
        sock.close()

    def send_file(self, filepath, sock):
        """
        The backend code for transmitting file over IIST net
        :param filepath: the valid filepath
        :param ip: the ip to which the file is to be sent
        :return: true if success, false if error
        """
        if os.path.isfile(filepath):
            with open(filepath,'r') as f:
                l = f.read(self.BUFFERSIZE)
                sock.send(l.encode())
        else:
            print('The given file path does not exist\n')
