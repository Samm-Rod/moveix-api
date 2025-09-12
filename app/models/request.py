from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.enums.request_status import TripRequestStatus, TypeFreight


"""
    Solicitação de viagem - dados puros da necessidade do cliente
    Persiste independente do matching
    """
class Request(Base):
    __tablename__="requests"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)

    # Dados da viagem
    distance = Column(Float, nullable=True)  # O sistema de estimativa vai devolver o valor calculado
    start_location = Column(String, nullable=False)# Local de partida []
    dropoff_location = Column(String, nullable=False)# Local de chegada []

    # Status da corrida

    # Características da carga
    volume_m3 = Column(Float, nullable=False)# Estimativa de volume m³  -   O modelo/IA via calcular
    freight_type = Column(SQLEnum(TypeFreight), nullable=False)# Tipo de frete []
    cargo_description = Column(Text, nullable=True)# descrição da carga []

    estimated_fare = Column(Float, nullable=True)

    # Timing
    is_scheduled = Column(Boolean, default=False)   # Agendado ? []
    requested_pickup_time = Column(DateTime, nullable=True) # Agendar data []
    flexible_time_window = Column(Integer, nullable=True)   # minutos de flexibilidade []

    """
        # Sistema calcula janela: 13:30 até 14:30
        # Busca motoristas disponíveis nessa janela toda
        # Oferece desconto de 10%
        # Motorista pode escolher melhor horário dentro da janela
    """

    # Status e metadata
    status = Column(String, default=TripRequestStatus.DRAFT.value)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    expires_at = Column(DateTime, nullable=True)  # Request expira se não encontrar motorista

    # Relacionamento 1:1
    client = relationship("Client", back_populates="request")
    matching = relationship("Matching", back_populates="request", uselist=False)
    # execution = relationship("Execution", back_populates="request", uselist=False)
