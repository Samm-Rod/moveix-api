# app/schemas/quote.py

from pydantic import BaseModel, Field
from typing import List

class QuoteOption(BaseModel):
    driver_id: int = Field(..., description="ID do motorista")
    driver_name: str = Field(..., description="Nome do motorista")
    vehicle: str | None = Field(None, description="Placa ou modelo do veículo")
    distance_km: float = Field(..., description="Distância em km")
    duration_min: float = Field(..., description="Duração em minutos")
    estimated_fare: float = Field(..., description="Valor estimado do frete")

class QuoteResponse(BaseModel):
    origin: str = Field(..., description="Endereço de partida formatado pelo Google")
    destination: str = Field(..., description="Endereço de destino formatado pelo Google")
    distance_km: float = Field(..., description="Distância total em km")
    duration_min: float = Field(..., description="Duração total em minutos")
    options: List[QuoteOption] = Field(..., description="Lista de motoristas e preços")
