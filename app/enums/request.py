from enum import Enum

class RequestStatus(str, Enum):
    DRAFT = "draft"         # Rascunho
    ACTIVE = "active"       # Ativo
    COMPLETED = "completed" # Completo
    CANCELLED = "cancelled" # Cancelado


    """
        Como é calculado o metro cúbico ? 
        Sei lá acho que sai caro de mais 
        essa corrida aí fiz um calculo de 
        como ele fizesse esse serviço 2x 
        dia e ganhasse 105 por serviço ele 
        teria mais de 7k no fim do mes kkkk 
        pensei em uma taxa base de R$ 70 + (R$1*m³) 
        pra não elevar o preço dos cliente, e como vai 
        ficar quem descide quem que vai precisar de ajudantes
    """