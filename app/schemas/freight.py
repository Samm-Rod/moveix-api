from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.enums.freight_status import FreightType, FreightStatus

class FreightBase(BaseModel):
    client_id: int
    pickup_address: str
    delivery_address: str
    freight_type: str
    estimated_weight: Optional[float] = None
    estimated_volume: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class FreightCreate(FreightBase):
    pass

class FreightRequest(BaseModel):
    origin_address: str
    destination_address: str
    freight_type: FreightType
    scheduled_time: Optional[datetime] = None
    volume: Optional[float] = None
    description: str
    is_round_trip: bool = False
    has_helpers_needed: bool = False

class FreightResponse(BaseModel):
    id: int
    client_id: int
    driver_id: Optional[int] = None
    status: FreightStatus
    pickup_address: str
    delivery_address: str
    pickup_lat: float
    pickup_lng: float
    delivery_lat: float
    delivery_lng: float
    freight_type: str
    estimated_weight: Optional[float] = None
    estimated_volume: Optional[float] = None
    estimated_price: float
    final_price: Optional[float] = None
    created_at: datetime
    accepted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True
        
class FreightStatusResponse(BaseModel):
    freight: FreightResponse
    matching: Optional[Dict[str, Any]] = None
    driver: Optional[Dict[str, Any]] = None
    current_status: str

class FreightUpdate(BaseModel):
    status: Optional[FreightStatus] = None
    final_price: Optional[float] = None
    current_location: Optional[Dict[str, Any]] = None

class FreightList(BaseModel):
    freights: List[FreightResponse]

class NearbyFreight(BaseModel):
    freight: FreightResponse
    distance_to_pickup: float  # Distância do motorista até o local