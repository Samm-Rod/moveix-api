from pydantic import BaseModel, ConfigDict
from typing import Optional

class PaymentCreate(BaseModel):
    ride_id: int
    amount: float
    payment_method: str 
    

class PaymentOut(BaseModel):
    id: int
    ride_id: int
    amount: float
    status: str
    fake_payment_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)