from sqlalchemy import Boolean, Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    user_role = Column(String, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    