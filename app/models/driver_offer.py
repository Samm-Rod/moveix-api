from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.enums.request_status import TripRequestStatus

class DriverOffer(Base):
    """
    Cada oferta individual para um motorista
    """
    __tablename__ = "driver_offers"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    helper_id = Column(Integer, ForeignKey('helpers.id'), nullable=False)

    # Dados da oferta
    offered_price = Column(Float, nullable=False)
    estimated_pickup_time = Column(DateTime, nullable=False)
    compatibility_score = Column(Float, nullable=False)
    offer_expires_at = Column(DateTime, nullable=False)

    # Resposta do motorista
    response = Column(SQLEnum(TripRequestStatus), nullable=True)  # 'accepted', 'declined', 'timeout'
    response_time = Column(DateTime, nullable=True)
    decline_reason = Column(String, nullable=True)
    response_time_seconds = Column(Integer, nullable=True)

    sent_at = Column(DateTime, default=datetime.now)

    # Relacionamentos
    matching = relationship("Matching", back_populates="driver_offers")
    driver = relationship("Driver", back_populates="driver_offers")
    helper = relationship("Helper", back_populates="driver_offers")
