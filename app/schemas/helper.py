from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.schemas.driver import Driver

class HelperBase(BaseModel):
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
    rating: Optional[float] = 5.0
    is_active: Optional[bool] = True   
    is_blocked: Optional[bool] = False

class HelperCreate(HelperBase):
    password: str

class HelperUpdate(BaseModel):
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
    is_blocked: Optional[bool] = None

class Helper(HelperBase):
    id: int
    created_at: datetime
    updated_at: datetime
    Drivers: List["Driver"] = []  # 👈 aspas aqui

    model_config = ConfigDict(from_attributes=True)

class HelperList(Helper):
    Helpers: List["Helper"] = []

    model_config = ConfigDict(from_attributes=True)


class HelperResponse(BaseModel):
    helper_id: int
    access_token: str
    token_type: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class HelperDeleteResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)

class HelperLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

class HelperLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

