from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VehicleBase(BaseModel):
    model: str
    brand: str  # agora obrigatório
    plate: str
    color: Optional[str] = None
    license_category: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass  # driver_id removido, brand obrigatório

class VehicleUpdate(BaseModel):
    model: Optional[str] = None
    brand: Optional[str] = None
    plate: Optional[str] = None
    color: Optional[str] = None
    license_category: Optional[str] = None

class Vehicle(VehicleBase):
    id: int
    driver_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None  # Torna updated_at opcional

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

class VehicleChoose(BaseModel):    
    vehicle: Vehicle

    class Config:
        from_attributes = True