# app/models/matching.py
from typing import Optional

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.enums.request_status import TripRequestStatus
from app.enums.matching_status import MatchingStatus  # Criar enum específico

"""
Processo de matching - foco no algoritmo e histórico
Só existe quando o request está ativo para matching
"""
class Matching(Base):

    __tablename__="matching"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey('requests.id'), nullable=False)

    # Estado do matching
    matching_status = Column(String, default=TripRequestStatus.SEARCHING.value)
    # searching -> drivers_found -> offers_sent -> matched -> confirmed -> failed

    failure_reason = Column(String, nullable=True)  # Por que falhou

    # Parâmetros de busca
    search_radius_km = Column(Float, default=25.0)      # Raio de busca começa a partir de 25km
    max_search_radius_km = Column(Float, default=100.0) # Raio máximo
    min_driver_rating = Column(Float, nullable=True) # Avaliação mínima
    preferred_vehicle_types = Column(Text, nullable=True)  # JSON array ["van", "truck"]
    """
    Tentativa 1: Raio 25km, rating > 4.5 → 0 motoristas
    Tentativa 2: Raio 50km, rating > 4.0 → 2 motoristas  
    Tentativa 3: Raio 100km, rating > 3.5 → 8 motoristas
    """

    # Resultados do matching
    drivers_found_count = Column(Integer, default=0)  # Quantos encontrou
    offers_sent_count = Column(Integer, default=0)  # Quantos receberam oferta
    declined_count = Column(Integer, default=0)  # Quantos recusaram

    # Driver selecionado
    selected_driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=True)
    selected_vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=True)
    match_score = Column(Float, nullable=True)
    matched_price = Column(Float, nullable=True)

    # Timeline
    started_at = Column(DateTime, default=datetime.now) # Data
    first_offer_sent_at = Column(DateTime, nullable=True)
    matched_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)

    # Métricas
    total_search_time_seconds = Column(Integer, nullable=True)
    average_response_time_seconds = Column(Float, nullable=True)

    # Relacionamentos
    request = relationship("Request", back_populates="matching")
    selected_driver = relationship("Driver")
    selected_vehicle = relationship("Vehicle")
    driver_offers = relationship("DriverOffer", back_populates="matching")

    """Matching está ativo?"""
    @property
    def is_active(self) -> bool:
        active_statuses = [MatchingStatus.SEARCHING, MatchingStatus.DRIVERS_FOUND, MatchingStatus.OFFERS_SENT]
        return self.matching_status in active_statuses

    """Tempo decorrido desde o início"""
    @property
    def elapsed_time_seconds(self) -> Optional[int]:
        if self.started_at:
            return int((datetime.now() - self.started_at).total_seconds())
        return None

    @property
    def success_rate(self) -> Optional[float]:
        """Taxa de sucesso das ofertas"""
        if self.offers_sent_count > 0:
            successful = self.offers_sent_count - self.declined_count - self.timeout_count
            return successful / self.offers_sent_count
        return None

    def set_failed(self, reason: str):
        """Marcar matching como falhou"""
        self.matching_status = MatchingStatus.FAILED
        self.failed_at = datetime.now()
        self.failure_reason = reason
        self.total_search_time_seconds = self.elapsed_time_seconds

    def set_matched(self, driver_id: int, vehicle_id: int, price: float, score: float):
        """Marcar como matched"""
        self.matching_status = MatchingStatus.MATCHED
        self.matched_at = datetime.now()
        self.selected_driver_id = driver_id
        self.selected_vehicle_id = vehicle_id
        self.matched_price = price
        self.match_score = score

    def set_confirmed(self):
        """Marcar como confirmado"""
        self.matching_status = MatchingStatus.CONFIRMED
        self.confirmed_at = datetime.now()
        self.total_search_time_seconds = self.elapsed_time_seconds




