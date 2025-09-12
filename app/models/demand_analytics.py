# app/models/demand_analytics.py
from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean
from datetime import datetime
from app.db.database import Base

class DemandAnalytics(Base):
    __tablename__ = 'demand_analytics'
    
    id = Column(Integer, primary_key=True)
    region = Column(String(100), nullable=False)  # "brasilia_centro", "goiania_norte"
    hour = Column(Integer, nullable=False)  # 0-23
    day_of_week = Column(Integer, nullable=False)  # 0=segunda, 6=domingo
    date = Column(DateTime, nullable=False)
    
    # Métricas de demanda
    total_requests = Column(Integer, default=0)
    completed_rides = Column(Integer, default=0)
    available_drivers = Column(Integer, default=0)
    average_wait_time = Column(Float, default=0)
    
    # Multiplicadores calculados
    demand_multiplier = Column(Float, default=1.0)
    supply_multiplier = Column(Float, default=1.0)
    final_surge_multiplier = Column(Float, default=1.0)
    
    # Fatores externos
    weather_impact = Column(Float, default=1.0)  # Chuva = +30%
    event_impact = Column(Float, default=1.0)    # Show, jogo = +50%
    
    created_at = Column(DateTime, default=datetime.now)