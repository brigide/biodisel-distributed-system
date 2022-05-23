from enum import Enum

class RequestTypes(str, Enum):
    Fill = 'Fill'

class Substances(str, Enum):
    Oil = 'Oil'
    NaOH = 'NaOH'
    EtOH = 'EtOH'

class States(str, Enum):
    Available = 'Available'
    Busy = 'Busy'