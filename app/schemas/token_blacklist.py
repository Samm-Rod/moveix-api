# app/schemas/token_blacklist.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TokenBlacklistBase(BaseModel):
    tokens: str
    user_id: int
    user_role: str
    expires_at: datetime

class TokenBlacklistCreate(TokenBlacklistBase):
    pass

class TokenBlacklistResponse(TokenBlacklistBase):
    id: int
    blacklisted_at: datetime

    model_config = ConfigDict(from_attributes=True)

