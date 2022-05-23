from src.servers.server import Server
from src.helpers.helpers import ServerHelper
from src.helpers import ports
from src.helpers.enums import RequestTypes, Substances, States

import json
import _thread
import socket
import time


class Reactor(Server):
    def __init__(self, host, port, name):
        super().__init__(host, port, name)

        self.oilAmount = 0
        self.naOHAmout = 0
        self.etOHAmount = 0
        self.totalAmount = 0
        self.decantedSolution = 0
        self.state = States.Available

        _thread.start_new_thread(self.process, ())

    def fillReactor(self, request):
        if self.state != States.Available:
            return {'status': False, 'message': 'component is busy'}
        else:
            if request['substance'] == Substances.Oil:
                self.oilAmount += request['amount']
                self.totalAmount += request['amount']
                return {'status': True, 'message': f'{Substances.Oil} received'}

            elif request['substance'] == Substances.NaOH:
                self.naOHAmout += request['amount']
                self.totalAmount += request['amount']
                return {'status': True, 'message': f'{Substances.NaOH} received'}

            elif request['substance'] == Substances.EtOH:
                self.etOHAmount += request['amount']
                self.totalAmount += request['amount']
                return {'status': True, 'message': f'{Substances.EtOH} received'}

        return {'status': False, 'message': 'invalid input'}

    def run(self, conn, addr):
        while True:
            request = json.loads(ServerHelper.waitMessage(conn))

            if request['type'] == RequestTypes.Fill:
                response = self.fillReactor(request)
                ServerHelper.sendMessage(conn, json.dumps(response))
                # print()
                # print(f'Oil amount: {self.oilAmount}')
                # print(f'NaOH amount: {self.naOHAmout}')
                # print(f'EtOH amount: {self.etOHAmount}')
                # print(f'Total: {self.oilAmount + self.naOHAmout + self.etOHAmount}')

    def process(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((ports.Decanter.Host(), ports.Decanter.Port()))
            except OSError as message:
                print('socket connection error: ' + str(message))
                print('retrying in 3 seconds...\n')
                time.sleep(3)
                self.process()

            while True:
                time.sleep(1)
                # if ((self.oilAmount * 100) / self.totalAmount == 50 
                # and (self.naOHAmout * 100) / self.totalAmount == 25 
                # and (self.etOHAmount * 100) / self.totalAmount == 25) or ((
                #     self.oilAmount + self.naOHAmout + self.etOHAmount > 5
                #     ) and (self.oilAmount >= 2.5 and self.naOHAmout >= 1.25 and self.etOHAmount >=1.25)):
                if self.oilAmount >= 2.5 and self.naOHAmout >= 1.25 and self.etOHAmount >= 1.25:
                    self.transferToDecanter(sock)


    def transferToDecanter(self, sock):
        processedSubstanceAmount = self.oilAmount + self.etOHAmount + self.naOHAmout
        if processedSubstanceAmount > 5:
            processedSubstanceAmount = 5

        request = {
            'type': RequestTypes.Fill,
            'substance': Substances.DecanterSolution,
            'amount': processedSubstanceAmount
        }

        # send request and get response
        sock.sendall(json.dumps(request).encode())

        response = json.loads(sock.recv(1024).decode())

        if response['status']:
            self.oilAmount -= (processedSubstanceAmount * 50) / 100
            self.naOHAmout -= (processedSubstanceAmount * 25) / 100
            self.etOHAmount -= (processedSubstanceAmount * 25) / 100
            self.totalAmount -= processedSubstanceAmount

