# app/schemas/quote.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from app.schemas.freight import FreightType

class QuoteResponse(BaseModel):
    base_price: float = Field(..., description="Preço base do frete")
    final_price: float = Field(..., description="Preço final do frete")
    distance_km: float = Field(..., description="Distância em km")
    duration_minutes: float = Field(..., description="Duração em minutos")
    freight_type: FreightType = Field(..., description="Tipo do frete")
    volume_m3: float = Field(..., description="Volume em metros cúbicos")
    origin: Optional[str] = Field(None, description="Endereço de partida formatado")
    destination: Optional[str] = Field(None, description="Endereço de destino formatado")
    duration_min: float = Field(..., description="Duração total em minutos")



class PriceBreakdown(BaseModel):
    demand_factor: float = Field(..., description="Fator baseado na demanda")
    time_factor: float = Field(..., description="Fator baseado no horário")
    weather_factor: float = Field(..., description="Fator baseado no clima")
    event_factor: float = Field(..., description="Fator baseado em eventos")
    surge_factor: float = Field(..., description="Fator de aumento dinâmico")

class DynamicQuoteResponse(QuoteResponse):
    surge_multiplier: float = Field(..., description="Multiplicador de preço dinâmico")
    breakdown: PriceBreakdown = Field(..., description="Detalhamento do cálculo do preço")
    explanation: str = Field(..., description="Explicação do preço dinâmico")
    valid_until: datetime = Field(..., description="Validade da cotação")
    
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
