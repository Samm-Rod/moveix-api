# app/schemas/matching_schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.enums.matching_status import MatchingStatus


# ===== REQUEST SCHEMAS =====

class StartMatchingRequest(BaseModel):
    """Iniciar matching"""
    request_id: int
    search_radius_km: Optional[float] = 25.0
    min_driver_rating: Optional[float] = None
    matching_status: MatchingStatus



class SelectDriverRequest(BaseModel):
    """Selecionar motorista"""
    driver_id: int
    vehicle_id: int
    price: float
    score: Optional[float] = 0.8


# ===== RESPONSE SCHEMAS =====

class MatchingResponse(BaseModel):
    """Resposta principal do matching"""
    matching_id: int
    request_id: int
    status: str

    # Resultados
    drivers_found: Optional[int] = None
    offers_sent: Optional[int] = None
    declined_count: Optional[int] = None

    # Driver selecionado
    selected_driver_id: Optional[int] = None
    matched_price: Optional[float] = None

    # Timeline
    started_at: Optional[datetime] = None
    matched_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    # Extras
    failure_reason: Optional[str] = None
    message: Optional[str] = None
    elapsed_seconds: Optional[int] = None

    class Config:
        from_attributes = True


class MatchingProgressResponse(BaseModel):
    """Progresso em tempo real"""
    status: str
    message: str
    progress_percentage: int  # 0-100

    drivers_found: Optional[int] = None
    offers_sent: Optional[int] = None
    elapsed_seconds: Optional[int] = None
    matching_id: Optional[int] = None

    is_completed: bool = False
    can_cancel: bool = True


class MatchingStatsResponse(BaseModel):
    """Estatísticas básicas"""
    period_days: int
    total_matchings: int
    successful_matchings: int
    failed_matchings: int
    success_rate: float  # %

    avg_search_time_seconds: float
    avg_drivers_found: float
    avg_offers_sent: float


# ===== WEBHOOK =====

class DriverResponseWebhook(BaseModel):
    """Resposta do motorista"""
    offer_id: int
    driver_id: int
    response: str  # "accepted" ou "declined"
    reason: Optional[str] = None


# ===== UTILITÁRIO =====

def matching_to_response(matching) -> MatchingResponse:
    """Converte model para response"""
    return MatchingResponse(
        matching_id=matching.id,
        request_id=matching.request_id,
        status=matching.matching_status,
        drivers_found=matching.drivers_found_count,
        offers_sent=matching.offers_sent_count,
        declined_count=matching.declined_count,
        selected_driver_id=matching.selected_driver_id,
        matched_price=matching.matched_price,
        started_at=matching.started_at,
        matched_at=matching.matched_at,
        confirmed_at=matching.confirmed_at,
        failed_at=matching.failed_at,
        failure_reason=matching.failure_reason,
        elapsed_seconds=matching.elapsed_time_seconds
    )