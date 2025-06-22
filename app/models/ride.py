from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Ride(Base):
    __tablename__ = 'rides'

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)

    start_location = Column(String, nullable=False)
    end_location = Column(String, nullable=False)
    distance = Column(Float, nullable=False)   # km
    duration = Column(Float, nullable=False)   # minutos
    fare = Column(Float, nullable=False)       # moeda local
    status = Column(String, default='pending') # ex: pending, em_andamento, finalizada, cancelada

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    # app/models/ride.py
    # Relacionamentos
    driver = relationship("Driver", back_populates="rides")
    client = relationship("Client", back_populates="rides")
    vehicle = relationship("Vehicle", back_populates="rides")

    def __repr__(self):
        return f"<Ride(id={self.id}, driver_id={self.driver_id}, client_id={self.client_id})>"
