import socket
from helpers import ports
import time
import random
import json

from helpers.enums import RequestTypes, Substances, States

class Orchestrator:
    def __init__(self):
        self.conns = {}
        self.conns['OilTank'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['Reactor'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['NaOHTank'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['EtOHTank'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['Decanter'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['EtOHDryer'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['GlycerinTank'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def addConn(self, name, host, port):
        try:
            self.conns[name].connect((host, port))
            print(f'{name} connected')

        except OSError as message:
            print(f'{name} connection error: {str(message)}')
            print('retrying in 3 seconds...\n')
            time.sleep(3)
            self.addConn(name, host, port)

    def addConns(self):
        self.addConn('OilTank', ports.OilTank.Host(), ports.OilTank.Port())
        self.addConn('GlycerinTank', ports.GlycerinTank.Host(), ports.GlycerinTank.Port())
        self.addConn('Decanter', ports.Decanter.Host(), ports.Decanter.Port())
        self.addConn('Reactor', ports.Reactor.Host(), ports.Reactor.Port())
        self.addConn('NaOHTank', ports.NaOHTank.Host(), ports.NaOHTank.Port())
        self.addConn('EtOHTank', ports.EtOHTank.Host(), ports.EtOHTank.Port())
        self.addConn('EtOHDryer', ports.EtOHDryer.Host(), ports.EtOHDryer.Port())
        


    def initialize(self):
        seconds = 0
        while True:
            print(seconds)
            time.sleep(1)
            seconds += 1


            naOHFill = {
                'type': RequestTypes.Fill,
                'substance': Substances.NaOH,
                'amount': 0.5
            }
            etOHFill = {
                'type': RequestTypes.Fill,
                'substance': Substances.EtOH,
                'amount': 0.25
            }
            
            self.conns['NaOHTank'].sendall(json.dumps(naOHFill).encode())
            response = self.conns['NaOHTank'].recv(1024).decode()

            self.conns['EtOHTank'].sendall(json.dumps(etOHFill).encode())
            response = self.conns['EtOHTank'].recv(1024).decode()

            if seconds % 10 == 0:
                request = {
                    'type': RequestTypes.Fill,
                    'substance': Substances.Oil,
                    'amount': random.uniform(1, 2)
                }
                
                self.conns['OilTank'].sendall(json.dumps(request).encode())
                response = self.conns['OilTank'].recv(1024).decode()


orchestrator = Orchestrator()
orchestrator.addConns()

orchestrator.initialize()