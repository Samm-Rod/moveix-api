from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class DriverMeta(Base):
    __tablename__ = "driver_meta"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, unique=True)

    latitude = Column(Float, nullable=True, default=-23.55052)
    longitude = Column(Float, nullable=True, default=-46.633309)
    is_available: Column[bool] = Column(Boolean, default=True, nullable=True)
    is_online: Column[bool] = Column(Boolean, default=True, nullable=True)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    rating = Column(Float, default=5.0, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    driver = relationship("Driver", back_populates="meta")