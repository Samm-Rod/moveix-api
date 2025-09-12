from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    cpf = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)

    # relacionamentos com sub-models
    auth = relationship("ClientAuth", back_populates="client", uselist=False, cascade="all, delete")
    meta = relationship("ClientMeta", back_populates="client", uselist=False, cascade="all, delete")
    rides = relationship("Ride", back_populates="client", cascade="all, delete")
    request = relationship("Request", back_populates="client", cascade="all, delete")

    def __repr__(self):
        return f"<Client(name={self.name}, email={self.email})>"
