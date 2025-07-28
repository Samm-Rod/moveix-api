from pydantic import BaseModel, EmailStr, Field, ConfigDict
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

    model_config = ConfigDict(from_attributes=True) 

class ClientLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

class ClientList(BaseModel):    
    clients: List[Client] = []

    model_config = ConfigDict(from_attributes=True)

class ClientResponse(BaseModel):    
    client_id: int
    access_token: str
    token_type: str
    message: str

    model_config = ConfigDict(from_attributes=True)

class ClientDeleteResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)

        