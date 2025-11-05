from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FreightRating(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Avaliação de 1 a 5 estrelas")
    comment: Optional[str] = None

class FreightRatingOut(BaseModel):
    id: int
    freight_id: int
    client_id: int
    rated_user_id: int  # ID do motorista ou ajudante avaliado
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    user_type: str  # "driver" ou "helper"

    class Config:
        from_attributes = True
