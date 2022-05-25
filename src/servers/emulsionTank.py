from src.servers.server import Server
from src.helpers.helpers import ServerHelper
from src.helpers import ports
from src.helpers.enums import RequestTypes, Substances, States

import json
import _thread
import socket
import time

class EmulsionTank(Server):
    def __init__(self, host, port, name):
        super().__init__(host, port, name)

        self.emulsionAmount = 0
        self.state = States.Available

    def fillTank(self, request):
        if self.state != States.Available:
            return {'status': False, 'message': 'component is busy'}
        else:
            if request['substance'] == Substances.Emulsion:
                self.emulsionAmount += request['amount']
                return {'status': True, 'message': 'input received'}

        return {'status': False, 'message': 'invalid input'}
                

    def run(self, conn, addr):
        while True:
            request = json.loads(ServerHelper.waitMessage(conn))

            if request['type'] == RequestTypes.Fill:
                response = self.fillTank(request)
                ServerHelper.sendMessage(conn, json.dumps(response))

            if request['type'] == RequestTypes.Report:
                response = {
                    'name': self.name,
                    'substances': {'Emulsion': self.emulsionAmount},
                    'volume': self.emulsionAmount,
                    'waste': 0,
                    'state': self.state
                }
                ServerHelper.sendMessage(conn, json.dumps(response))