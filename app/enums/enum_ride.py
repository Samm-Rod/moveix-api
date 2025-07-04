from enum import Enum

class RideStatus(str, Enum):
    DISPONIVEL = "disponivel"
    ACEITA = "aceita"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelled"

class Service_type(str, Enum):
    RESIDENCIAL = "residencial"
    COMERCIAL = "comercial"
    INDUSTRIAL = "industrial"