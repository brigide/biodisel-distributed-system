from src.servers.oilTank import OilTank
from src.servers.reactor import Reactor
from src.servers.naOHTank import NaOHTank
from src.servers.etOHTank import EtOHTank
from src.helpers import ports

import _thread


class Main:
    def __init__(self):
        self.processes = {}
        self.threads = {}

    def addProcesses(self):
        self.processes['OilTank'] = OilTank(ports.OilTank.Host(), ports.OilTank.Port(), 'OilTank')
        conn, addr = self.processes['OilTank'].waitConnection()
        self.threads['OilTank'] = _thread.start_new_thread(self.processes['OilTank'].run, (conn, addr))
        #self.threads['OilTankOutputs'] = _thread.start_new_thread(self.processes['OilTank'].outputs, ())

        
        self.processes['Reactor'] = Reactor(ports.Reactor.Host(), ports.Reactor.Port(), 'Reactor')
        conn, addr = self.processes['Reactor'].waitConnection()
        self.threads['Reactor'] = _thread.start_new_thread(self.processes['Reactor'].run, (conn, addr))
        conn, addr = self.processes['Reactor'].waitConnection()
        self.threads['Reactor'] = _thread.start_new_thread(self.processes['Reactor'].run, (conn, addr))

        self.processes['NaOHTank'] = NaOHTank(ports.NaOHTank.Host(), ports.NaOHTank.Port(), 'NaOHTank')
        conn, addr = self.processes['NaOHTank'].waitConnection()
        self.threads['NaOHTank'] = _thread.start_new_thread(self.processes['NaOHTank'].run, (conn, addr))
        conn, addr = self.processes['Reactor'].waitConnection()
        self.threads['Reactor'] = _thread.start_new_thread(self.processes['Reactor'].run, (conn, addr))

        self.processes['EtOHTank'] = EtOHTank(ports.EtOHTank.Host(), ports.EtOHTank.Port(), 'EtOHTank')
        conn, addr = self.processes['EtOHTank'].waitConnection()
        self.threads['EtOHTank'] = _thread.start_new_thread(self.processes['EtOHTank'].run, (conn, addr))
        conn, addr = self.processes['Reactor'].waitConnection()
        self.threads['Reactor'] = _thread.start_new_thread(self.processes['Reactor'].run, (conn, addr))

        while True:
            continue



if __name__ == '__main__':
    Main().addProcesses()