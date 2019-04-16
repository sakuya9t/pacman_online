import socket


class socReceiver():
    def __init__(self, host, port):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((host, port))
        self.soc.listen(10)
        print 'listening'
        self.connection, soc_addr = self.soc.accept() #blocked

    def receiveData(self):
        return self.connection.recv(1024)

    def closeSocket(self):
        self.soc.close()
