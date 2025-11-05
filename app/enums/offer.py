# 'accepted', 'declined', 'timeout'
from enum import Enum

class DriverOfferStatus(Enum):
    DRAFT = "draft"                    # Rascunho (cliente ainda criando)
    PENDING = "pending"  # Aguardando encontrar motorista
    MATCHED = "matched"                # Motorista encontrado mas não confirmou
    CONFIRMED = "confirmed"            # Motorista confirmou
    IN_PROGRESS = "in_progress"        # Em execução
    COMPLETED = "completed"            # Finalizada
    CANCELLED = "cancelled"            # Cancelada
    EXPIRED = "expired"                # Expirou sem matching
    SEARCHING = "searching"            # Buscando
    FAILED = "failed"                  # Nenhum motorista disponível
    DRIVERS_FOUND = "drivers_found"
    OFFERS_SENT = "offers_sent"
    DECLINED = "declined"
    ACCEPTED = "accepted"
    TIMEOUT = "timeout"