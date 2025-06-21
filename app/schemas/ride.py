from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

class RideBase(BaseModel):
    driver_id: int
    client_id: int
    start_location: str = Field(..., min_length=1, max_length=255)
    end_location: str = Field(..., min_length=1, max_length=255)
    distance: float  # in kilometers
    duration: float  # in minutes
    fare: float  # in local currency
    status: Optional[str] = 'pending'  # e.g., pending, completed, cancelled

class RideCreate(RideBase):
    pass

class RideUpdate(RideBase):
    driver_id: Optional[int] = None
    client_id: Optional[int] = None
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[float] = None
    fare: Optional[float] = None
    status: Optional[str] = None

class Ride(RideBase):
    id: int
    created_at: datetime
    updated_at: datetime

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

