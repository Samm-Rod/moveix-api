# app/models/surge_zone.py
from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean
from datetime import datetime
from app.db.database import Base

class SurgeZone(Base):
    __tablename__ = 'surge_zones'
    
    id = Column(Integer, primary_key=True)
    zone_name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    
    # Coordenadas da zona (polígono simplificado)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_km = Column(Float, default=5.0)
    
    # Multiplicadores atuais
    current_multiplier = Column(Float, default=1.0)
    updated_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)