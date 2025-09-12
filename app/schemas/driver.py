from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional, List
from app.schemas.vehicle import Vehicle
from app.schemas.helper import HelperResponse
from app.utils.validators import validate_cpf
import logging

logger = logging.getLogger(__name__)


# ----------------------------
# Base
# ----------------------------
class DriverBase(BaseModel):
    """Campos básicos de motorista (entrada e base para respostas)."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    birth_date: date
    phone: Optional[str] = None
    cpf: Optional[str] = Field(None, min_length=11, max_length=11, description="CPF sem pontuação")
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    rating: float = 5.0
    is_active: bool = True   
    has_helpers: bool = False
    helper_price: Optional[float] = None
    is_blocked: bool = False

    @field_validator("cpf")
    def check_cpf(cls, v):
        if not validate_cpf(v):
            logger.warning(f"CPF inválido : {v}")
            raise ValueError("CPF inválido")
        logger.info(f"CPF válido : {v}")
        return v

# ----------------------------
# Create & Update
# ----------------------------
class DriverCreate(DriverBase):
    password: str = Field(..., min_length=6)
    car_model: str
    car_plate: str
    car_color: str
    driver_license: str
    license_category: str


class DriverUpdate(BaseModel):
    """Update parcial, todos campos opcionais."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = None
    is_active: Optional[bool] = None  
    has_helpers: Optional[bool] = None
    helper_price: Optional[float] = None
    is_blocked: Optional[bool] = None

    @field_validator("*", mode="before")
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

# ----------------------------
# Respostas (saída)
# ----------------------------
class DriverResponseBase(DriverBase):
    """Campos retornados ao consultar motorista."""
    id: int
    created_at: datetime
    updated_at: datetime
    vehicles: List[Vehicle] = []

    model_config = ConfigDict(from_attributes=True)


class DriverResponse(BaseModel):
    id: int
    name: str
    email: str
    cpf: str
    meta: Optional['DriverMetaResponse']  # include se quiser created/updated

    model_config = ConfigDict(from_attributes=True)

class DriverMetaResponse(BaseModel):
    rating: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProfileBase(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

class DriverProfile(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    rating: Optional[float] = 5.0
    is_active: Optional[bool] = True
    vehicle_plate: Optional[str] = None  # se tiver apenas 1 veículo principal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DriverList(BaseModel):
    """Lista de motoristas."""
    drivers: List[DriverResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Helpers favoritos
# ----------------------------
class FavoriteHelpersResponse(BaseModel):
    helpers: List[HelperResponse] = []

    model_config = ConfigDict(from_attributes=True)


class AddFavoriteHelper(BaseModel):
    helper_id: int


class DeleteFavoriteHelper(BaseModel):
    helper_id: int


# ----------------------------
# Autenticação
# ----------------------------
class DriverLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class DriverAuthResponse(BaseModel):
    driver_id: int
    access_token: str
    token_type: str = "bearer"
    message: str = "Motorista autenticado com sucesso."

    model_config = ConfigDict(from_attributes=True)


class DriverDeleteResponse(BaseModel):
    message: str = "Motorista removido com sucesso."

    model_config = ConfigDict(from_attributes=True)
