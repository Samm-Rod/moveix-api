from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime


class Vehicle(Base):
    __tablename__='vehicles'

    id = Column(Integer, primary_key=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)

    model = Column(String, nullable=False)         # Ex: 'Corolla 2020'
    brand = Column(String, nullable=False)         # Ex: 'Toyota'
    color = Column(String, nullable=True)          # Ex: 'Preto'
    plate = Column(String, unique=True, nullable=False)  # Ex: 'ABC-1234'
    license_category = Column(String, nullable=True)


    chassis = Column(String, unique=True, nullable=True) # opcional: segurança
    tracker_enabled = Column(Boolean, default=False)     # se tem rastreador
    active = Column(Boolean, default=True)               # veículo ativo ou não
    created_at = Column(DateTime, default=datetime.now)

    # app/models/vehicles.py
    driver = relationship("Driver", back_populates="vehicles")
    rides = relationship("Ride", back_populates="vehicle", cascade="all, delete")
