# app/models/matching.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Optional
from app.db.database import Base
from app.enums.matching_status import MatchingStatus


class Matching(Base):
    __tablename__ = "matchings"  # Plural para consistência

    id = Column(Integer, primary_key=True, index=True)
    freight_id = Column(Integer, ForeignKey("freights.id"), nullable=True)  # Mudei de request_id
    driver_offer_id = Column(Integer, ForeignKey("driver_offers.id"), nullable=True)

    # Estado do matching
    status = Column(SQLEnum(MatchingStatus), default=MatchingStatus.SEARCHING)
    failure_reason = Column(String, nullable=True)

    # Parâmetros de busca
    search_radius_km = Column(Float, default=5.0)  # Começar menor, expandir se necessário
    max_search_radius_km = Column(Float, default=50.0)
    min_driver_rating = Column(Float, default=3.0)
    preferred_vehicle_types = Column(Text, nullable=True)

    # Resultados
    drivers_found_count = Column(Integer, default=0)
    offers_sent_count = Column(Integer, default=0)
    declined_count = Column(Integer, default=0)
    timeout_count = Column(Integer, default=0)  # Campo que estava faltando

    # Match final
    selected_driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=True)
    selected_vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=True)
    match_score = Column(Float, nullable=True)
    matched_price = Column(Float, nullable=True)

    # Timeline
    # use callable default with UTC timezone
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    first_offer_sent_at = Column(DateTime, nullable=True)
    matched_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)

    # Métricas
    total_search_time_seconds = Column(Integer, nullable=True)
    average_response_time_seconds = Column(Float, nullable=True)

    # Relationships
    freights = relationship("Freight", back_populates="matching")
    driver_offers = relationship("DriverOffer", back_populates="matching")
    selected_driver = relationship("Driver", foreign_keys=[selected_driver_id])
    selected_vehicle = relationship("Vehicle", foreign_keys=[selected_vehicle_id])

    # Properties corrigidas
    @property
    def is_active(self) -> bool:
        # compare enum members directly (not their .value)
        active_statuses = {
            MatchingStatus.SEARCHING,
            MatchingStatus.DRIVERS_FOUND,
            MatchingStatus.OFFERS_SENT,
        }
        return self.status in active_statuses

    @property
    def elapsed_time_seconds(self) -> Optional[int]:
        if self.started_at:
            started = self.started_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            return int((datetime.now(timezone.utc) - started).total_seconds())
        return None

    @property
    def success_rate(self) -> Optional[float]:
        if (self.offers_sent_count or 0) > 0:
            successful = (self.offers_sent_count or 0) - (self.declined_count or 0) - (self.timeout_count or 0)
            return max(0.0, successful) / float(self.offers_sent_count)
        return None

    def set_failed(self, reason: str) -> None:
        self.status = MatchingStatus.FAILED
        self.failed_at = datetime.now(timezone.utc)
        self.failure_reason = reason
        self.total_search_time_seconds = self.elapsed_time_seconds

    def set_matched(self, driver_id: int, vehicle_id: int, price: float, score: float):
        self.status = MatchingStatus.MATCHED
        self.matched_at = datetime.now(timezone.utc)
        self.selected_driver_id = driver_id
        self.selected_vehicle_id = vehicle_id
        self.matched_price = price
        self.match_score = score

    def set_finished(self):
        self.status = MatchingStatus.COMPLETED

    def set_confirmed(self):
        self.status = MatchingStatus.CONFIRMED
        self.confirmed_at = datetime.now(timezone.utc)
        self.total_search_time_seconds = self.elapsed_time_seconds
