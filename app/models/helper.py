from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base

class Helper(Base):
    __tablename__ = "helpers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    birth_date = Column(DateTime, nullable=True)
    phone = Column(String, nullable=True)
    cpf = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)

    # relacionamento com drivers
    drivers = relationship("Driver", secondary="drivers_helpers", back_populates="helpers")

    # relacionamentos com sub-models
    auth = relationship("HelperAuth", back_populates="helper", uselist=False, cascade="all, delete")
    meta = relationship("HelperMeta", back_populates="helper", uselist=False, cascade="all, delete")
    search_helpers = relationship("SearchHelper", back_populates="helper")
    driver_offers = relationship("DriverOffer", back_populates="helper")

    def __repr__(self):
        return f"<Helper(name={self.name}, email={self.email})>"




