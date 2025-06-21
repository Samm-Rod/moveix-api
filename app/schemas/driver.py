from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List
from app.schemas.vehicle import Vehicle

class DriverBase(BaseModel):
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

class DriverCreate(DriverBase):
    password: str
    car_model: str
    car_plate: str
    car_color: str
    driver_license: str
    license_category: str

class DriverUpdate(BaseModel): 
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

class Driver(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime
    vehicles: List[Vehicle] = []

    class Config:
        from_attributes = True

class DriverList(BaseModel):
    drivers: List[Driver] = []

    class Config:
        from_attributes = True

class DriverResponse(BaseModel):
    driver: Driver

    class Config:
        from_attributes = True

class DriverDeleteResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True

class DriverLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class DriverLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
