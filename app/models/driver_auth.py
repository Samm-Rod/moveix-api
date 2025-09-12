from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class DriverAuth(Base):
    __tablename__ = "driver_auth"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, unique=True)
    
    hashed_password = Column(String, nullable=False)
    two_fa_secret = Column(String, nullable=True)
    reset_code = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)

    driver = relationship("Driver", back_populates="auth")