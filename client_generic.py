from socket import *
import os

class generic_client():
    """
    Generic class code for the client end, which establishes communication with the server, and
    then co-ordinates activities among other clients in order to transfer and receive files.
    """

    def __init__(self, alias, serverIP='none', serverPort='none'):
        """
        The constructor of the generic class which at the moment takes only the alias name on
        creation and sets it efficiently as a class property
        :param alias: the alias name by which you are recognized online on the server
        """
        self.alias = alias
        self.BUFFERSIZE = 1024
        self.server_ip = serverIP
        self.server_port = serverPort

    @property
    def server_ip(self):
        return self._server_ip

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
        self.server_socket.send("alias : %s"%self.alias)
        reply = self.server_socket.recv(self.BUFFERSIZE)
        if reply is 'success':
            print('Successfully set alias name to %s\n'%self.alias)
            return False
        else:
            print('Alias name is unable to be set, Try again!\n')
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

