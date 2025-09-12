from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

# ----------------------------
# Base
# ----------------------------
class ClientBase(BaseModel):
    """Campos básicos para criação/atualização de cliente."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


# ----------------------------
# Criação & Update
# ----------------------------
class ClientCreate(ClientBase):
    password: str


class ClientUpdate(BaseModel):
    """Update parcial (todos os campos opcionais)."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


# ----------------------------
# Respostas (saída)
# ---------------------------



class ClientProfile(ClientBase):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    is_active: Optional[bool] = True

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ClientResponse(ClientProfile):
    """Resposta detalhada de um cliente."""

class ClientList(BaseModel):
    """Lista de clientes."""
    clients: List[ClientResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Autenticação
# ----------------------------
class ClientLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class ClientRegisterResponse(BaseModel):
    """Resposta ao cadastrar cliente com autenticação."""
    client_id: int
    access_token: str
    token_type: str
    message: str

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Outros
# ----------------------------
class ClientDeleteResponse(BaseModel):
    message: str = "Cliente removido com sucesso."

    model_config = ConfigDict(from_attributes=True)
