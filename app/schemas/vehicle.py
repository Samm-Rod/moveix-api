from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.enums.enum_vehicles import LicenseCategory, VehicleStatus, VehicleSize

class VehicleBase(BaseModel):
    model: str
    brand: str  # agora obrigatório
    plate: str
    color: Optional[str] = None
    license_category: LicenseCategory
    status: VehicleStatus
    size: VehicleSize  # pequeno, médio, grande

class VehicleCreate(VehicleBase):
    pass  # driver_id removido, brand obrigatório

# Atualiza veículo
class VehicleUpdate(BaseModel):
    model: Optional[str] = None
    brand: Optional[str] = None
    plate: Optional[str] = None
    color: Optional[str] = None
    license_category: LicenseCategory
    status: VehicleStatus
    size: VehicleSize

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