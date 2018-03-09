from clientGeneric import GenericClient

if __name__ == '__main__':
    sam = GenericClient(alias='Sam', serverIP ='172.20.113.190', serverPort=6000)
    sam.run_time()
