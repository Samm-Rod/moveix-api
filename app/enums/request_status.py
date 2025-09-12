from enum import Enum

class TripRequestStatus(Enum):
    DRAFT = "draft"                         # Rascunho (cliente ainda criando)
    PENDING_MATCHING = "pending_matching"   # Aguardando encontrar motorista
    MATCHED = "matched"                     # Motorista encontrado mas não confirmou
    CONFIRMED = "confirmed"                 # Motorista confirmou
    IN_PROGRESS = "in_progress"             # Em execução
    COMPLETED = "completed"                 # Finalizada
    CANCELED = "canceled"                   # Cancelada
    EXPIRED = "expired"                     # Expirou sem matching
    SEARCHING = "searching"                 # Buscando
    FAILED = "failed"                       # Nenhum motorista disponível


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



