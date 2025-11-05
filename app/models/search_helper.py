from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.database import Base
from app.enums.request_status import TripRequestStatus
from app.models.helper import Helper


class SearchHelper(Base):

    __tablename__="search_helper"
    """
    Motorista procura por ajudantes/helpers
    """
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    helper_id = Column(Integer, ForeignKey('helpers.id'), nullable=False)
    is_online = Column(Boolean, nullable=True, default=True)

    name = Column(String, nullable=True)
    rating = Column(Float, nullable=True)

    driver = relationship("Driver", back_populates="search_helpers")
    helper = relationship("Helper", back_populates="search_helpers")
