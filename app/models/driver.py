# app/models/driver.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
from app.models.drivers_helpers import drivers_helpers
from app.models.search_helper import SearchHelper

class Driver(Base):
    __tablename__ = "drivers"

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


    # relacionamentos com os novos modelos
    auth = relationship("DriverAuth", back_populates="driver", uselist=False, cascade="all, delete")
    meta = relationship("DriverMeta", back_populates="driver", uselist=False, cascade="all, delete")
    services = relationship("DriverServices", back_populates="driver", uselist=False, cascade="all, delete")
    search_helpers = relationship("SearchHelper", back_populates="driver")
    driver_offers = relationship("DriverOffer", back_populates="driver")

    # app/models/driver.py
    rides = relationship("Ride", back_populates="driver", cascade="all, delete")  # se ride tiver driver_id
    vehicles = relationship("Vehicle", back_populates="driver", cascade="all, delete")
    freights = relationship("Freight", back_populates="driver", cascade="all, delete")

    helpers = relationship("Helper", secondary=drivers_helpers, back_populates="drivers")

    def __repr__(self):
        return f"<Driver(name={self.name}, email={self.email})>"
