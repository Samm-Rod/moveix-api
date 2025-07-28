# app/models/helpers.py
from sqlalchemy import Column, ForeignKey, Integer, Float, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
from app.models.drivers_helpers import drivers_helpers

class Helper(Base):
    __tablename__ = 'helpers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    birth_date = Column(DateTime, nullable=True)
    phone = Column(String, nullable=True)
    cpf = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    rating = Column(Float, default=5.0, nullable=False)  # Avaliação
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    is_blocked = Column(Boolean, default=False, nullable=False)  # Bloqueado

    two_fa_secret = Column(String, nullable=True)  # 2FA
    reset_code = Column(String, nullable=True)     # Código de reset de senha

    # N:N drivers and Helpers
    drivers = relationship("Driver", secondary=drivers_helpers, back_populates="helpers")

    def __repr__(self):
        return f"<Helper(name={self.name}, email={self.email})>"




