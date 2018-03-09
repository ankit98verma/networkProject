from clientGeneric import GenericClient

if __name__ == '__main__':
    sam = GenericClient(alias='Sam', serverIP ='localhost', serverPort=5000)
    sam.run_time()
