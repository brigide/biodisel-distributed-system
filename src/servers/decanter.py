from src.servers.server import Server
from src.helpers.helpers import ServerHelper
from src.helpers import ports
from src.helpers.enums import RequestTypes, Substances, States

import json
import _thread
import socket
import time

class Decanter(Server):
    def __init__(self, host, port, name):
        super().__init__(host, port, name)

        self.solutionAmount = 0
        self.capacity = 10
        self.state = States.Available
        self.busyTime = 0

        _thread.start_new_thread(self.process, ())

    def fillDecanter(self, request):
        if self.state != States.Available:
            return {'status': False, 'message': 'component is busy'}
        else:
            if request['substance'] == Substances.DecanterSolution:
                if self.capacity >= self.solutionAmount + request['amount']:
                    self.solutionAmount += request['amount']
                    return {'status': True, 'message': f'{Substances.DecanterSolution} received entirely', 'back': 0}
                elif self.capacity < self.solutionAmount + request['amount'] and self.solutionAmount < self.capacity:
                    back = self.solutionAmount + request['amount'] - self.capacity
                    self.solutionAmount += request['amount'] - back
                    return {'status': True, 'message': f'{Substances.DecanterSolution} received partialy', 'back': back}
                elif self.solutionAmount >= self.capacity:
                    return {'status': False, 'message': f'Decanter is full', 'back': 0}
        return {'status': False, 'message': 'invalid input'}
                

    def run(self, conn, addr):
        while True:
            request = json.loads(ServerHelper.waitMessage(conn))

            if request['type'] == RequestTypes.Fill:
                response = self.fillDecanter(request)
                if response['status']:
                    print('recieved substance')
                    self.state = States.Busy
                ServerHelper.sendMessage(conn, json.dumps(response))

    def connectDryer(self):
        dryerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            dryerSocket.connect((ports.EtOHDryer.Host(), ports.EtOHDryer.Port()))
            return dryerSocket
        except OSError as message:
                print('socket connection error: ' + str(message))
                print('retrying in 3 seconds...\n')
                time.sleep(3)
                self.connectDryer()

    def connectGlycerinTank(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ports.GlycerinTank.Host(), ports.GlycerinTank.Port()))
            return sock
        except OSError as message:
                print('socket connection error: ' + str(message))
                print('retrying in 3 seconds...\n')
                time.sleep(3)
                self.connectGlycerinTank()

    def connectWashing1(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ports.Washing1.Host(), ports.Washing1.Port()))
            return sock
        except OSError as message:
                print('socket connection error: ' + str(message))
                print('retrying in 3 seconds...\n')
                time.sleep(3)
                self.connectWashing1()


    def process(self):
        dryerSocket = self.connectDryer()
        glycerinSocket = self.connectGlycerinTank()
        washingSocket = self.connectWashing1()
        print(f'decanter connected to dryer')
        

        while True:
            time.sleep(1)
            if self.state != States.Busy:
                self.transferEtOHToDryer(dryerSocket)
                self.transferToGlycerinTank(glycerinSocket)
                self.transferToWashing1(washingSocket)
            else:
                print('decanter is busy')
                if self.busyTime >= 5:
                    self.state = States.Available
                    self.busyTime = 0
                else:
                    self.busyTime += 1


    def transferEtOHToDryer(self, sock):
        sendingAmount = 0
        if self.solutionAmount > 1:
            sendingAmount = (1 * 3) / 100
        else:
            sendingAmount = (self.solutionAmount * 3) / 100
            
        request = {
            'type': RequestTypes.Fill,
            'substance': Substances.EtOH,
            'amount': sendingAmount
        }

        # send request and get response
        sock.sendall(json.dumps(request).encode())

        response = json.loads(sock.recv(1024).decode())

        if response['status']:
            self.solutionAmount -= sendingAmount

    def transferToGlycerinTank(self, sock):
        sendingAmount = 0
        if self.solutionAmount > 1:
            sendingAmount = (1 * 1) / 100
        else:
            sendingAmount = (self.solutionAmount * 1) / 100
            
        request = {
            'type': RequestTypes.Fill,
            'substance': Substances.Glycerin,
            'amount': sendingAmount
        }

        # send request and get response
        sock.sendall(json.dumps(request).encode())

        response = json.loads(sock.recv(1024).decode())

        if response['status']:
            self.solutionAmount -= sendingAmount

    def transferToWashing1(self, sock):
        sendingAmount = 0
        if self.solutionAmount > 1:
            sendingAmount = (1 * 96) / 100
        else:
            sendingAmount = (self.solutionAmount * 96) / 100
            
        request = {
            'type': RequestTypes.Fill,
            'substance': Substances.EtOH,
            'amount': sendingAmount
        }

        # send request and get response
        sock.sendall(json.dumps(request).encode())

        response = json.loads(sock.recv(1024).decode())

        if response['status']:
            self.solutionAmount -= sendingAmount




