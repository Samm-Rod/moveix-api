from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.enums.request_status import TripRequestStatus, TypeFreight

class RequestRideBase(BaseModel):
    start_location: str = Field(..., min_length=1, max_length=255)
    dropoff_location: str = Field(..., min_length=1, max_length=255)
    volume_m3: float
    freight_type: TypeFreight
    cargo_description: str
    is_scheduled: bool
    requested_pickup_time: datetime  # "14:00"
    flexible_time_window: int  # 60 min


class RequestRide(RequestRideBase):
    pass

class RequestGetById(RequestRideBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UpdateRide(RequestRide):
    start_location: Optional[str] = Field(None, min_length=1, max_length=255)
    dropoff_location: Optional[str] = Field(None, min_length=1, max_length=255)
    volume_m3: Optional[float] = None
    freight_type: Optional[TypeFreight] = None
    cargo_description: Optional[str] = None
    is_scheduled: Optional[bool] = None
    requested_pickup_time: Optional[datetime] = None
    flexible_time_window: Optional[int] = None


class RequestCanceled(BaseModel):
    model_config = ConfigDict(from_attributes=True)




