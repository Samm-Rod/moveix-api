from enum import Enum

class TripRequestStatus(Enum):
    DRAFT = "draft"                         # Rascunho (cliente ainda criando)
    PENDING = "pending"   # Aguardando encontrar motorista
    MATCHED = "matched"                     # Motorista encontrado mas não confirmou
    MATCHING = "matching"
    CONFIRMED = "confirmed"                 # Motorista confirmou
    IN_PROGRESS = "in_progress"             # Em execução
    COMPLETED = "completed"                 # Finalizada
    CANCELLED = "cancelled"                   # Cancelada
    EXPIRED = "expired"                     # Expirou sem matching
    SEARCHING = "searching"                 # Buscando
    FAILED = "failed"                       # Nenhum motorista disponível
    ACCEPTED = "accepted"
    TIMEOUT = "timeout"
    REJECTED = "rejected"
    FINISHED = "finished"
    STARTING = "starting"

class TypeFreight(Enum):
    CHANGE = "change" # Mudança
    FREIGHT = "freight" # Frete

class TypePayments(Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    PIX = "pix"

class Vehicles(Enum):
    CAR = "car"
    VAN = "van"
    TRUCK_SMALL = "truck_small"
    TRUCK_MEDIUM = "truck_medium"
    TRUCK_LARGE = "truck_large"



