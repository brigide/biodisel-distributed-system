from unittest.mock import sentinel
from src.servers.server import Server
from src.helpers.helpers import ServerHelper
from src.helpers import ports
from src.helpers.enums import RequestTypes, Substances, States

import json
import _thread
import socket
import time

class EtOHDryer(Server):
    def __init__(self, host, port, name):
        super().__init__(host, port, name)

        self.etOHAmount = 0
        self.waste = 0
        self.state = States.Available

        _thread.start_new_thread(self.process, ())

    def fillDryer(self, request):
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
                    response = self.fillDryer(request)
                    ServerHelper.sendMessage(conn, json.dumps(response))

                if request['type'] == RequestTypes.Report:
                    response = {
                        'name': self.name,
                        'substances': {'EtOH': self.etOHAmount},
                        'volume': self.etOHAmount,
                        'waste': self.waste,
                        'state': self.state
                    }
                    ServerHelper.sendMessage(conn, json.dumps(response))

    def process(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((ports.EtOHTank.Host(), ports.EtOHTank.Port()))
                print(f'dryer connected to etoh tank')
            except OSError as message:
                print('socket connection error: ' + str(message))
                print('retrying in 3 seconds...\n')
                time.sleep(3)
                self.process()

            while True:
                time.sleep(5)
                self.transferToEtOHTank(sock)


    def transferToEtOHTank(self, sock):
        sendingAmount = 0
        if self.etOHAmount > 1:
            sendingAmount = 1
        else:
            return

        sendingAmount -= (sendingAmount * 0.5) / 100
            
        request = {
            'type': RequestTypes.Fill,
            'substance': Substances.EtOH,
            'amount': sendingAmount
        }

        # send request and get response
        sock.sendall(json.dumps(request).encode())

        response = json.loads(sock.recv(1024).decode())

        if response['status']:
            self.etOHAmount -= sendingAmount + (sendingAmount * 0.5) / 100
            self.waste += (sendingAmount * 0.5) / 100




