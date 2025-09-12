# app/models/driver_services.py
from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class DriverServices(Base):
    __tablename__ = "driver_services"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, unique=True)

    has_helpers = Column(Boolean, default=False, nullable=False)
    helper_price = Column(Float, nullable=True)

    driver = relationship("Driver", back_populates="services")