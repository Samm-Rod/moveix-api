from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class HelperMeta(Base):
    __tablename__ = "helper_meta"

    id = Column(Integer, primary_key=True, index=True)
    helper_id = Column(Integer, ForeignKey("helpers.id"), nullable=False, unique=True)

    rating = Column(Float, default=5.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now(), nullable=False)

    helper = relationship("Helper", back_populates="meta")