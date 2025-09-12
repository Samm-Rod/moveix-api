# app/schemas/quote.py

from pydantic import BaseModel, Field
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime

class QuoteOption(BaseModel):
    driver_id: int = Field(..., description="ID do motorista")
    driver_name: str = Field(..., description="Nome do motorista")
    vehicle_model: str | None = Field(None, description="Modelo ou modelo do veículo")
    vehicle_color: str | None = Field(None, description="Cor ou modelo do veículo")
    vehicle_plate: str | None = Field(None, description="Placa ou modelo do veículo")
    distance_km: float = Field(..., description="Distância em km")
    duration_min: float = Field(..., description="Duração em minutos")
    estimated_fare: float = Field(..., description="Valor estimado do frete")

class QuoteResponse(BaseModel):
    origin: str = Field(..., description="Endereço de partida formatado pelo Google")
    destination: str = Field(..., description="Endereço de destino formatado pelo Google")
    distance_km: float = Field(..., description="Distância total em km")
    duration_min: float = Field(..., description="Duração total em minutos")
    options: List[QuoteOption] = Field(..., description="Lista de motoristas e preços")




class PriceBreakdown(BaseModel):
    demand_factor: float
    time_factor: float
    weather_factor: float
    event_factor: float
    surge_factor: float

class DynamicQuoteResponse(BaseModel):
    base_price: float
    final_price: float
    surge_multiplier: float
    distance_km: float
    duration_minutes: float
    freight_type: str
    
    breakdown: PriceBreakdown
    explanation: str
    valid_until: datetime
    
    # Visual indicators
    is_surge_active: bool = False
    surge_level: str = "normal"  # "low", "normal", "high", "very_high"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def __init__(self, **data):
        super().__init__(**data)
        
        # Determinar nível de surge
        if self.surge_multiplier >= 2.0:
            self.surge_level = "very_high"
            self.is_surge_active = True
        elif self.surge_multiplier >= 1.5:
            self.surge_level = "high" 
            self.is_surge_active = True
        elif self.surge_multiplier >= 1.2:
            self.surge_level = "medium"
            self.is_surge_active = True
        elif self.surge_multiplier <= 0.9:
            self.surge_level = "discount"
        else:
            self.surge_level = "normal"
