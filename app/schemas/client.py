from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List   

class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class ClientCreate(ClientBase):
    password: str    

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class Client(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

class ClientLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class ClientList(BaseModel):    
    clients: List[Client] = []

    class Config:
        from_attributes = True 

class ClientResponse(BaseModel):    
    client: Client

    class Config:
        from_attributes = True

class ClientDeleteResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True

        