import socket

class Server():
    def __init__(self, host, port, name=''):
        self.host = host
        self.port = port
        self.name = name
        self.socket = ""
        self.initSocket()
        #self.connect()

        #self.waitConnection()

    def initSocket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(8)
        #self.socket.setblocking(False)

        print(f'{self.name} server listening on port: ' + str(self.port))


    def waitConnection(self):
        """
            now it accepts connections 
        """
        conn, addr = self.socket.accept()
        print('\n' + str(addr) + ' connected')
        return conn, addr


    def closeServer(self):
        #closes server's socket
        self.socket.close()