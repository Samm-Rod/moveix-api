from pydantic import BaseModel, ConfigDict
from datetime import datetime 

class LocationBase(BaseModel):
    ride_id: int 
    latitude: str
    longitude: str


class LocationResponse(LocationBase):
    pass

class LocationRead(LocationBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationCreate(BaseModel):
    latitude: float
    longitude: float