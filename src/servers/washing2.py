from src.servers.server import Server
from src.helpers.helpers import ServerHelper
from src.helpers import ports
from src.helpers.enums import RequestTypes, Substances, States

import json
import _thread
import socket
import time

class Washing2(Server):
    def __init__(self, host, port, name):
        super().__init__(host, port, name)

        self.etOHAmount = 0
        self.state = States.Available

        _thread.start_new_thread(self.process, ())

    def fillWasher(self, request):
        if self.state != States.Available:
            return {'status': False, 'message': 'component is busy'}
        else:
            if request['substance'] == Substances.EtOH:
                self.etOHAmount += request['amount']
                return {'status': True, 'message': f'{Substances.EtOH} received'}
        return {'status': False, 'message': 'invalid input'}
                

    def run(self, conn, addr):
        while True:
            request = ServerHelper.waitMessage(conn)
            if True: #type(request) == dict:
                request = json.loads(request)

                if request['type'] == RequestTypes.Fill:
                    response = self.fillWasher(request)
                    ServerHelper.sendMessage(conn, json.dumps(response))

    def connectNextWasher(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ports.Washing3.Host(), ports.Washing3.Port()))
            return sock
        except OSError as message:
                print('socket connection error: ' + str(message))
                print('retrying in 3 seconds...\n')
                time.sleep(3)
                self.connectNextWasher()

    def connectEmulsionTank(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ports.EmulsionTank.Host(), ports.EmulsionTank.Port()))
            return sock
        except OSError as message:
                print('socket connection error: ' + str(message))
                print('retrying in 3 seconds...\n')
                time.sleep(3)
                self.connectEmulsionTank()

    def process(self):
        washerSock = self.connectNextWasher()
        emulsionSock = self.connectEmulsionTank()
        print(f'whaser 2')
        

        while True:
            time.sleep(1)
            self.transferToNextWasher(washerSock)
            self.transferToEmulsionTank(emulsionSock)


    def transferToNextWasher(self, sock):
        sendingAmount = 0
        if self.etOHAmount > 1.5:
            sendingAmount = 1.5
        else:
            sendingAmount = self.etOHAmount

        sendingAmount -= (sendingAmount * 2.5) / 100
            
        request = {
            'type': RequestTypes.Fill,
            'substance': Substances.EtOH,
            'amount': sendingAmount
        }

        # send request and get response
        sock.sendall(json.dumps(request).encode())

        response = json.loads(sock.recv(1024).decode())

        if response['status']:
            self.etOHAmount -= sendingAmount + (sendingAmount * 2.5) / 100

    def transferToEmulsionTank(self, sock):
        emulsion = 0
        if self.etOHAmount > 1.5:
            emulsion = 1.5
        else:
            emulsion = self.etOHAmount

        sendingAmount = (emulsion * 2.5) / 100
            
        request = {
            'type': RequestTypes.Fill,
            'substance': Substances.Emulsion,
            'amount': sendingAmount
        }

        # send request and get response
        sock.sendall(json.dumps(request).encode())

        response = json.loads(sock.recv(1024).decode())

        if response['status']:
            self.etOHAmount -= sendingAmount 




