# app/models/freight_status.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from datetime import datetime, timezone
from app.db.database import Base
from app.enums.freight_status import FreightStatus


class Freight(Base):
    __tablename__ = "freights"

    # Primary Keys
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)

    # Status
    status = Column(SQLEnum(FreightStatus, name="freightstatus"), default=FreightStatus.PENDING)

    # Location Data (separado do JSON para queries eficientes)
    pickup_address = Column(Text, nullable=False)
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    delivery_address = Column(Text, nullable=False)
    delivery_lat = Column(Float, nullable=False)
    delivery_lng = Column(Float, nullable=False)

    # Cargo Info
    freight_type = Column(String, nullable=False)
    estimated_weight = Column(Float)
    estimated_volume = Column(Float)

    # Pricing
    estimated_price = Column(Float)
    final_price = Column(Float, nullable=True)

    # Additional Data (use JSONB instead of JSON for better performance)
    request_metadata = Column(JSONB, nullable=True)  # Dados extras do request
    current_location = Column(JSONB, nullable=True)

    # Timeline
    # use a callable to set the default at insert time (UTC)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    accepted_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="freights")
    driver = relationship("Driver", back_populates="freights")
    matching = relationship("Matching", back_populates="freights")

    def __repr__(self):
        return f"<Freight(id={self.id}, status={self.status})>"