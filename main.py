from clientGeneric import GenericClient

if __name__ == '__main__':
    sam = GenericClient(alias='Sam', serverIP ='127.0.0.1', serverPort=5000)
    sam.run_time()
