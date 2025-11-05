from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.db.database import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    freight_id = Column(Integer, ForeignKey("freights.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    rated_user_id = Column(Integer)  # ID do motorista ou ajudante avaliado
    rating = Column(Integer)  # 1-5 estrelas
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime)
    user_type = Column(String)  # "driver" ou "helper"
