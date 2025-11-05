from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.enums.matching_status import MatchingStatus

class DriverOfferBase(BaseModel):
    matching_id: int
    driver_id: int
    freight_id: int
    offered_price: float

class DriverOfferResponse(BaseModel):
    id: int
    matching_id: int
    driver_id: int
    freight_id: int
    offered_price: float
    status: MatchingStatus
    created_at: datetime
    expires_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True

class DriverOfferResponseRequest(BaseModel):
    accepted: bool