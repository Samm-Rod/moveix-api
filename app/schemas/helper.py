from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.driver import DriverResponse
# ----------------------------
# Base
# ----------------------------
class HelperBase(BaseModel):
    """Campos básicos do ajudante."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    birth_date: date
    phone: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    rating: float = 5.0
    is_active: Optional[bool] = True
    is_blocked: Optional[bool] = False


# ----------------------------
# Create & Update
# ----------------------------
class HelperCreate(HelperBase):
    password: str


class HelperUpdate(BaseModel):
    """Update parcial, todos campos opcionais."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = True
    is_blocked: Optional[bool] = False


# ----------------------------
# Respostas (saída)
# ----------------------------
class HelperResponseBase(HelperBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HelperUpdateResponse(HelperBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HelperProfile(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HelperResponse(HelperResponseBase):
    """Resposta detalhada de um ajudante."""
    drivers: List["DriverResponse"] = []


class HelperList(BaseModel):
    id: int
    helpers: List[HelperResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Avaliação
# ----------------------------
class EvaluateHelper(BaseModel):
    rating: int = Field(..., ge=0, le=5, description="Avaliação de 0 a 5")

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Autenticação
# ----------------------------
class HelperLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class HelperAuthResponse(BaseModel):
    helper_id: int
    access_token: str
    token_type: str = "bearer"
    message: str = "Ajudante autenticado com sucesso."

    model_config = ConfigDict(from_attributes=True)


class HelperDeleteResponse(BaseModel):
    message: str = "Ajudante removido com sucesso."

    model_config = ConfigDict(from_attributes=True)
