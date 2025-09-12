# app/services/token_blacklist_service.py
from sqlalchemy.orm import Session
from app.models.token import TokensBlacklist
from app.schemas.token_blacklist import TokenBlacklistCreate
from datetime import datetime


def add_token_to_blacklist(db: Session, token_data: TokenBlacklistCreate):
    token = TokensBlacklist(
        tokens=token_data.tokens,
        user_id=token_data.user_id,
        user_role=token_data.user_role,
        expires_at=token_data.expires_at,
        blacklisted_at=datetime.now()
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token

def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(TokensBlacklist).filter(TokensBlacklist.tokens == token).first() is not None
