from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.enums.matching_status import MatchingStatus


# --- Base ---
class MatchingBase(BaseModel):
    request_id: int
    matching_status: MatchingStatus = MatchingStatus.SEARCHING
    failure_reason: Optional[str] = None

    search_radius_km: float = 25.0
    max_search_radius_km: float = 100.0
    min_driver_rating: Optional[float] = None
    preferred_vehicle_types: Optional[str] = None  # pode ser JSON string


# --- Create ---
class MatchingCreate(MatchingBase):
    pass


# --- Update ---
class MatchingUpdate(BaseModel):
    matching_status: Optional[MatchingStatus] = None
    failure_reason: Optional[str] = None
    selected_driver_id: Optional[int] = None
    selected_vehicle_id: Optional[int] = None
    match_score: Optional[float] = None
    matched_price: Optional[float] = None
    drivers_found_count: Optional[int] = None
    offers_sent_count: Optional[int] = None
    declined_count: Optional[int] = None


# --- Response ---
class MatchingResponse(BaseModel):
    id: int
    freight_id: int
    status: MatchingStatus
    failure_reason: Optional[str] = None
    search_radius_km: float
    max_search_radius_km: float
    min_driver_rating: float
    preferred_vehicle_types: Optional[str] = None
    drivers_found_count: int
    offers_sent_count: int
    declined_count: int
    timeout_count: int
    selected_driver_id: Optional[int] = None
    selected_vehicle_id: Optional[int] = None
    match_score: Optional[float] = None
    matched_price: Optional[float] = None
    started_at: datetime
    first_offer_sent_at: Optional[datetime] = None
    matched_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    total_search_time_seconds: Optional[int] = None
    average_response_time_seconds: Optional[float] = None
    is_active: bool
    elapsed_time_seconds: Optional[int] = None
    success_rate: Optional[float] = None

    class Config:
        from_attributes = True
        use_enum_values = True
