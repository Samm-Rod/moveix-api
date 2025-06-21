from sqlalchemy import Column, Integer, Float, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

"""
-> Cadastrar motorista:
   - Nome completo
   - Data de nascimento
   - CPF
   - E-mail
   - Telefone
   - Cidade e Estado
"""

class Driver(Base):
    __tablename__ = 'drivers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    birth_date = Column(DateTime, nullable=True)
    cpf = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    rides = relationship("Ride", back_populates="driver", cascade="all, delete")  # se ride tiver driver_id
    vehicles = relationship("Vehicle", back_populates="driver", cascade="all, delete")

    def __repr__(self):
        return f"<Driver(name={self.name}, email={self.email})>"
