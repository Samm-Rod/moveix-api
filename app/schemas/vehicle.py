from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.enums.enum_vehicles import LicenseCategory, VehicleStatus, VehicleSize

class VehicleBase(BaseModel):
    model: str = Field(..., min_length=1)
    brand: str = Field(..., min_length=1)
    plate: str = Field(..., pattern=r"^[A-Z]{3}-\d{4}$", description="Formato: ABC-1234")
    color: Optional[str] = None
    license_category: LicenseCategory
    status: VehicleStatus
    size: VehicleSize

class VehicleCreate(VehicleBase):
    pass  # driver_id removido, brand obrigatório

# Atualiza veículo
class VehicleUpdate(BaseModel):
    model: Optional[str] = None
    brand: Optional[str] = None
    plate: Optional[str] = None
    color: Optional[str] = None
    license_category: Optional[LicenseCategory] = None
    status: Optional[VehicleStatus] = None
    size: Optional[VehicleSize] = None

class Vehicle(VehicleBase):
    id: int
    driver_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None  # Torna updated_at opcional

    model_config = ConfigDict(from_attributes=True)

# Remove um veículo
class VehicleRemove(Vehicle):  # se quiser devolver dados completos após deletar
    message: str

# Listar veículos
class VehicleList(BaseModel):
    vehicles: List[Vehicle]

    model_config = ConfigDict(from_attributes=True)

class VehicleResponse(BaseModel):    
    vehicle: Vehicle

    model_config = ConfigDict(from_attributes=True)

# Escolhe veículo
class VehicleChoose(BaseModel):    
    vehicle: Vehicle

    model_config = ConfigDict(from_attributes=True)