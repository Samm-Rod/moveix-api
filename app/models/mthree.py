""""
    O M3 é um algoritmo de inteligência artificial que calcula volume em metros cúbicos
    de objetos e transforma em no total da de volumes e total de peso estimado para transporte e retorna
    o veículo adequado e valor calculado
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.database import Base

class MThree(Base):

    __tablename__="mthree"
    ...