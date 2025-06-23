from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RideBase(BaseModel):
    start_location: str = Field(..., min_length=1, max_length=255)
    end_location: str = Field(..., min_length=1, max_length=255)
    distance: float  # in kilometers
    duration: float  # in minutes
    fare: float  # in local currency

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

