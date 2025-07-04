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

class RideCreate(RideBase):
    pass  # Não exige client_id, driver_id, vehicle_id nem status

class RideUpdate(RideBase):
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[float] = None
    fare: Optional[float] = None
    status: Optional[str] = None
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    rating: Optional[int] = None  # Avaliação de 0 a 5
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
    rating: Optional[int] = None  # Avaliação de 0 a 5

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

class RideRating(BaseModel):
    rating: int = Field(..., ge=0, le=5, description="Avaliação de 0 a 5")

    class Config:
        from_attributes = True


class RideBooking(RideBase):
    driver_id: int
