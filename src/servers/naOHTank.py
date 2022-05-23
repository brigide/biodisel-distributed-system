from src.servers.server import Server
from src.helpers.helpers import ServerHelper
from src.helpers import ports
from src.helpers.enums import RequestTypes, Substances, States

import json
import _thread
import socket
import time

class NaOHTank(Server):
    def __init__(self, host, port, name):
        super().__init__(host, port, name)

        self.naOHAmount = 0
        self.state = States.Available

        _thread.start_new_thread(self.process, ())

    def fillTank(self, request):
        if self.state != States.Available:
            return {'status': False, 'message': 'component is busy'}
        else:
            if request['substance'] == Substances.NaOH:
                self.naOHAmount += request['amount']
                return {'status': True, 'message': 'input received'}

        return {'status': False, 'message': 'invalid input'}
                

    def run(self, conn, addr):
        while True:
            request = json.loads(ServerHelper.waitMessage(conn))

            if request['type'] == RequestTypes.Fill:
                response = self.fillTank(request)
                ServerHelper.sendMessage(conn, json.dumps(response))

    def process(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((ports.Reactor.Host(), ports.Reactor.Port()))
            except OSError as message:
                print('socket connection error: ' + str(message))
                print('retrying in 3 seconds...\n')
                time.sleep(3)
                self.process()

            while True:
                time.sleep(1)
                self.transferNaOHToReactor(sock)


    def transferNaOHToReactor(self, sock):
        sendingAmount = 0
        if self.naOHAmount > 1:
            sendingAmount = 1
        else:
            sendingAmount = self.naOHAmount
            
        request = {
            'type': RequestTypes.Fill,
            'substance': Substances.NaOH,
            'amount': sendingAmount
        }

        # send request and get response
        sock.sendall(json.dumps(request).encode())

        response = json.loads(sock.recv(1024).decode())

        if response['status']:
            self.naOHAmount -= sendingAmount




