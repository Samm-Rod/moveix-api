from enum import Enum

class FreightType(Enum):
    MOVING = "moving"      # Mudança
    FREIGHT = "freight"    # Carga
    DELIVERY = "delivery"  # Entrega

class FreightStatus(Enum):
    ACCEPTED = "accepted"               # Motorista aceitou
    STARTING = "starting"               # Iniciando no ponto de partida
    DRAFT = "draft"                     # Rascunho (cliente ainda criando)
    PENDING = "pending"                 # Aguardando encontrar motorista
    MATCHED = "matched"                 # Motorista encontrado mas não confirmou
    CONFIRMED = "confirmed"             # Motorista confirmou
    IN_PROGRESS = "in_progress"         # Em execução
    COMPLETED = "completed"             # Finalizada
    CANCELLED = "cancelled"             # Cancelada
    EXPIRED = "expired"                 # Expirou sem matching
    SEARCHING = "searching"             # Buscando
    FAILED = "failed"                   # Nenhum motorista disponível
    DRIVERS_FOUND = "drivers_found"
    OFFERS_SENT = "offers_sent"

class PaymentsType(Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    PIX = "pix"

class VehiclesType(Enum):
    CAR = "car"
    VAN = "van"
    TRUCK_SMALL = "truck_small"
    TRUCK_MEDIUM = "truck_medium"
    TRUCK_LARGE = "truck_large"