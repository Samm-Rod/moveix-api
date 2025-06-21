from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VehicleBase(BaseModel):
    model: str
    plate: str
    color: Optional[str] = None
    driver_license: Optional[str] = None
    license_category: Optional[str] = None

class VehicleCreate(VehicleBase):
    driver_id: int

class VehicleUpdate(BaseModel):
    model: Optional[str] = None
    plate: Optional[str] = None
    color: Optional[str] = None
    driver_license: Optional[str] = None
    license_category: Optional[str] = None



class Vehicle(VehicleBase):
    id: int
    driver_id: int 
    created_at: datetime
    updated_at: datetime 

    class Config:
        from_attributes = True

class VehicleRemove(Vehicle):  # se quiser devolver dados completos após deletar
    message: str

class VehicleList(BaseModel):
    vehicles: List[Vehicle]

    class Config: 
        from_attributes = True

class VehicleResponse(BaseModel):    
    vehicle: Vehicle

    class Config:
        from_attributes = True