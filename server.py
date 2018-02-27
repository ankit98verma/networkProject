from socket import *


def start():

    serverSoc = socket(AF_INET, SOCK_STREAM)

    serverSoc.bind((gethostname(), 5000))

    serverSoc.listen(10)

    

