from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class HelperAuth(Base):
    __tablename__ = "helper_auth"

    id = Column(Integer, primary_key=True, index=True)
    helper_id = Column(Integer, ForeignKey("helpers.id"), nullable=False, unique=True)

    hashed_password = Column(String, nullable=False)
    two_fa_secret = Column(String, nullable=True)
    reset_code = Column(String, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)

    helper = relationship("Helper", back_populates="auth")
