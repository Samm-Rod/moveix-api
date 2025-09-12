# app/services/matching_service.py
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.enums import TripRequestStatus
from app.models.matching import Matching
from app.schemas.matching_schemas import (
    StartMatchingRequest,
    SelectDriverRequest,
    MatchingResponse,
    MatchingProgressResponse,
    MatchingStatsResponse,
    matching_to_response,
)
from app.enums.matching_status import MatchingStatus
from app.models.request import Request

import logging

logger = logging.getLogger(__name__)

class MatchingService:
    def __init__(self, db: Session):
        self.db = db


    """Inicia um novo processo de matching para um request"""

    # Iniciar processo de matching
    def start_matching(self, request_id: int, request_data: StartMatchingRequest) -> MatchingResponse:
        logger.warning(f" 🎯 AQUI: {request_id}")
        logger.warning(f" 🎯 CAPTURA DO ID DA REQUISIÇÃO: {request_id}")
        request = self.db.query(Request).filter(Request.id == request_data.request_id).first()
        if not request:
            raise ValueError("Request não encontrado")

        existing_matching = (
            self.db.query(Matching)
            .filter(Matching.request_id == request.id)
            .filter(Matching.matching_status.in_([
                MatchingStatus.SEARCHING.value,
                MatchingStatus.DRIVERS_FOUND.value,
                MatchingStatus.OFFERS_SENT.value
            ])).first()
        )

        if existing_matching:
            logger.warning(f"MATCHING JÁ EXISTENTE ⚠️")
            return matching_to_response(existing_matching)


        matching = Matching(
            request_id=request.id,
            search_radius_km=request_data.search_radius_km,
            min_driver_rating=request_data.min_driver_rating,
            matching_status=TripRequestStatus.SEARCHING.value,
            started_at=datetime.now(),
        )

        self.db.add(matching)
        self.db.commit()
        self.db.refresh(matching)

        return matching_to_response(matching)

    def update_progress(self, matching_id: int, drivers_found: int, offers_sent: int) -> MatchingProgressResponse:
        matching = self.db.query(Matching).filter(Matching.id == matching_id).filter()
        if not matching:
            raise ValueError("Matching não encontrado")

        matching.drivers_found = drivers_found
        matching.offers_sent_count = offers_sent
        matching.offers_sent_count = offers_sent
        matching.matching_status = MatchingStatus.OFFERS_SENT
        self.db.commit()

        progress_percentage = min(100, (offers_sent * 10) + (drivers_found * 5))  # regra fictícia

        return MatchingProgressResponse(
                status=matching.matching_status,
                message="Progresso atualizado",
                progress_percentage=progress_percentage,
                drivers_found=drivers_found,
                offers_sent=offers_sent,
                elapsed_seconds=matching.elapsed_time_seconds,
                matching_id=matching.id,
                is_completed=matching.matching_status in [MatchingStatus.MATCHED, MatchingStatus.CONFIRMED, MatchingStatus.FAILED],
                can_cancel=matching.is_active,
        )

    # Selecionar motorista
    def select_driver(self, matching_id: int, data: SelectDriverRequest) -> MatchingResponse:
        matching = self.db.query(Matching).filter(Matching.id == matching_id).first()
        if not matching:
            raise ValueError("Matching não encontrado")

        matching.set_matched(
            driver_id=data.driver_id,
            vehicle_id=data.vehicle_id,
            price=data.price,
            score=data.score or 0.8,
        )
        self.db.commit()
        self.db.refresh(matching)

        return matching_to_response(matching)

    # Confirmar matching
    def confirm_matching(self, matching_id: int) -> MatchingResponse:
        matching = self.db.query(Matching).filter(Matching.id == matching_id).first()
        if not matching:
            raise ValueError("Matching não encontrado")

        matching.set_confirmed()
        self.db.commit()
        self.db.refresh(matching)

        return matching_to_response(matching)



    def fail_matching(self, matching_id: int, reason: str) -> MatchingResponse:
        matching = self.db.query(Matching).filter(Matching.id == matching_id).first()
        if not matching:
            raise ValueError("Matching não encontrado")

        matching.set_failed(reason)
        self.db.commit()
        self.db.refresh(matching)

        return matching_to_response(matching)

    def get_stats(self, period_days: int = 30) -> MatchingStatsResponse:
        q = self.db.query(Matching).filter(
            Matching.started_at >= datetime.now() - timedelta(days=period_days)
        )

        total = q.count()

        success = q.filter(Matching.matched_status == MatchingStatus.CONFIRMED).count()
        failed = q.filter(Matching.matching_status == MatchingStatus.FAILED).count()

        avg_search_time = q.with_entities(func.avg(Matching.total_search_time_seconds)).scalar() or 0
        avg_drivers = q.with_entities(func.avg(Matching.drivers_found_count)).scalar() or 0
        avg_offers = q.with_entities(func.avg(Matching.offers_sent_count)).scalar() or 0

        return MatchingStatsResponse(
            period_days=period_days,
            total_matchings=total,
            successful_matchings=success,
            failed_matchings=failed,
            success_rate=(success / total * 100) if total > 0 else 0,
            avg_search_time_seconds=avg_search_time,
            avg_drivers_found=avg_drivers,
            avg_offers_sent=avg_offers,
        )

    def get_progress(self, matching_id):
        pass