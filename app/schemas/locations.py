from pydantic import BaseModel
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

    class Config:
        from_attributes = True



