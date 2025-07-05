from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RideBase(BaseModel):
    start_location: str = Field(..., min_length=1, max_length=255)
    end_location: str = Field(..., min_length=1, max_length=255)
    distance: float  # in kilometers
    duration: float  # in minutes
    fare: float  # in local currency
    scheduled: bool = False
    freight_type: str = 'mudanca'
    volume: Optional[int] = None
    round_trip: bool = False

class RideOption(BaseModel):
    driver_id: int
    driver_name: str
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    vehicle_plate: Optional[str] = None
    distance_km: float
    duration_min: float
    estimated_fare: float

class RideQuoteResponse(BaseModel):
    origin: str
    destination: str
    distance_km: float
    duration_min: float
    options: List[RideOption]

class RideConfirmation(BaseModel):
    start_location: str = Field(..., alias="start_location")
    end_location: str = Field(..., alias="end_location")
    distance_km: float = Field(..., alias="distance")
    duration_min: float = Field(..., alias="duration")
    fare: float
    driver_id: int

class RideUpdate(RideBase):
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[float] = None
    fare: Optional[float] = None
    status: Optional[str] = None
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    rating: Optional[int] = None
    scheduled: Optional[bool] = None
    freight_type: Optional[str] = None
    volume: Optional[int] = None
    round_trip: Optional[bool] = None

class Ride(RideBase):
    id: int
    client_id: int
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    rating: Optional[int] = None

    class Config:
        from_attributes = True

class RideList(BaseModel):
    rides: List[Ride] = []

    class Config:
        from_attributes = True

class RideResponse(BaseModel):
    ride: Ride

    class Config:
        from_attributes = True

class RideDeleteResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True

class Evaluate_driver(BaseModel):
    rating: int = Field(..., ge=0, le=5, description="Avaliação de 0 a 5")

    class Config:
        from_attributes = True


class RideRatingOut(BaseModel):
    id: int
    client_id: int
    start_location: str
    end_location: str
    rating: int

    class Config:
        from_attributes = True

