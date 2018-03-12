from clientGeneric import GenericClient

if __name__ == '__main__':
    server_IP = input('Enter the Server IP : \n')
    if server_IP == '':
        server_IP = 'localhost'
    sam = GenericClient(alias='Sam', serverIP=server_IP, serverPort=5000)
    sam.run_time()
