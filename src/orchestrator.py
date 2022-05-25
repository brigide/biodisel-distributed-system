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
        self.conns['Washing1'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['Washing2'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['Washing3'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['EmulsionTank'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['BiodieselDryer'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conns['BiodieselTank'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        self.addConn('BiodieselTank', ports.BiodieselTank.Host(), ports.BiodieselTank.Port())
        self.addConn('BiodieselDryer', ports.BiodieselDryer.Host(), ports.BiodieselDryer.Port())
        self.addConn('EmulsionTank', ports.EmulsionTank.Host(), ports.EmulsionTank.Port())
        self.addConn('Washing3', ports.Washing3.Host(), ports.Washing3.Port())
        self.addConn('Washing2', ports.Washing2.Host(), ports.Washing2.Port())
        self.addConn('Washing1', ports.Washing1.Host(), ports.Washing1.Port())
        self.addConn('GlycerinTank', ports.GlycerinTank.Host(), ports.GlycerinTank.Port())
        self.addConn('EtOHDryer', ports.EtOHDryer.Host(), ports.EtOHDryer.Port())
        self.addConn('Decanter', ports.Decanter.Host(), ports.Decanter.Port())
        self.addConn('Reactor', ports.Reactor.Host(), ports.Reactor.Port())
        self.addConn('NaOHTank', ports.NaOHTank.Host(), ports.NaOHTank.Port())
        self.addConn('EtOHTank', ports.EtOHTank.Host(), ports.EtOHTank.Port())



    def initialize(self):
        seconds = 0
        while True:
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

            self.report(seconds)

    def report(self, seconds):
        print('\n' * 14)
        print(f'time elapsed: {self.secondsToHour(seconds)}' + ' ' * 50 + 'system status: working')
        print()

        #print header
        header = ['Component', 'State', 'Waste', 'Volume', 'Substances']
        for head in header:
            print(head.ljust(25), end='')
        print()

        self.getComponentReports()

    def secondsToHour(self, seconds):
        return time.strftime('%H:%M:%S', time.gmtime(seconds))

    def getComponentReports(self):
        self.printReport(self.getReport('OilTank'))
        self.printReport(self.getReport('NaOHTank'))
        self.printReport(self.getReport('EtOHTank'))
        self.printReport(self.getReport('Reactor'))
        self.printReport(self.getReport('Decanter'))
        glycerin = self.getReport('GlycerinTank')
        self.printReport(glycerin)
        self.printReport(self.getReport('EtOHDryer'))
        self.printReport(self.getReport('Washing1'))
        self.printReport(self.getReport('Washing2'))
        self.printReport(self.getReport('Washing3'))
        emulsion = self.getReport('EmulsionTank')
        self.printReport(emulsion)
        self.printReport(self.getReport('BiodieselDryer'))
        biodiesel = self.getReport('BiodieselTank')
        self.printReport(biodiesel)
        print('Glycerin generated: '.ljust(10), end='')
        print(glycerin['substances']['Glycerin'])
        print('Emulsion generated: '.ljust(10), end='')
        print(emulsion['substances']['Emulsion'])
        print('Biodiesel generated: '.ljust(10), end='')
        print(biodiesel['substances']['Biodiesel'])


    def printReport(self, component):
        keylist = list(component['substances'])
        print(component['name'].ljust(25), end='')
        print(component['state'].ljust(25), end='')
        print(str(round(component['waste'], 2)).ljust(25), end='')
        print(str(round(component['volume'], 2)).ljust(25), end='')
        print(keylist[0] + ': ' + str(round(component['substances'][keylist[0]], 2)).ljust(25), end='')
        if len(keylist) > 1:
            for i in range(1, len(keylist)):
                print((' ').ljust(25), end='')
                print(''.ljust(25), end='')
                print(''.ljust(25), end='')
                print(''.ljust(25), end=' ' * (len(component['name']) + i))
                print(keylist[i] + ': ' + str(round(component['substances'][keylist[i]], 2)).ljust(25), end='')
        print('\n' + '-' * 120)

    def getReport(self, name):
        request = {
            'type': RequestTypes.Report
        }
        
        self.conns[name].sendall(json.dumps(request).encode())
        response = self.conns[name].recv(1024).decode()
        response = json.loads(response)
        #response = json.loads(response['substances'])
        return response



orchestrator = Orchestrator()
orchestrator.addConns()

orchestrator.initialize()