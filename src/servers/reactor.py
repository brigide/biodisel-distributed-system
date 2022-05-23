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
        self.state = States.Available

        #_thread.start_new_thread(self.process, ())

    def fillReactor(self, request):
        if self.state != States.Available:
            return {'status': False, 'message': 'component is busy'}
        else:
            if request['substance'] == Substances.Oil:
                self.oilAmount += request['amount']
                return {'status': True, 'message': f'{Substances.Oil} received'}

            elif request['substance'] == Substances.NaOH:
                self.naOHAmout += request['amount']
                return {'status': True, 'message': f'{Substances.NaOH} received'}

            elif request['substance'] == Substances.EtOH:
                print('aaaaaaaa')
                self.etOHAmount += request['amount']
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

    #def process(self):


