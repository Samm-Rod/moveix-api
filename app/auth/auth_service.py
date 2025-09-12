# app/auth/auth_service.py
from datetime import timedelta, datetime
from jose import jwt, JWTError
from app.utils.config import SECRET_KEY, REFRESH_SECRET_KEY,ALGORITHM, ACCESS_tokens_EXPIRE_MINUTES, REFRESH_tokens_EXPIRE_MINUTES
from fastapi import HTTPException, status
from app.models.token import TokensBlacklist
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

def create_access_tokens(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_tokens_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def create_refresh_tokens(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=REFRESH_tokens_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})
    encode_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt
    
def decode_tokens(tokens: str):
    try:
        logger.debug(f"Decoding token (len={len(tokens)}): {tokens[:50]}...")
        print(f"Decoding token (len={len(tokens)}): {tokens[:50]}...")
        payload = jwt.decode(tokens, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Decoded payload: {payload}")
        return payload
    except JWTError as e:
        err_msg = str(e)
        logger.warning(f"Failed to decode token: {err_msg} (token_len={len(tokens)})")
        # Give more specific, safe error details for common problems to help debugging
        if 'Not enough segments' in err_msg:
            detail_msg = 'Token malformado ou truncado'
        elif 'Signature has expired' in err_msg or 'expired' in err_msg.lower():
            detail_msg = 'Token expirado'
        elif 'Signature verification failed' in err_msg or 'invalid signature' in err_msg.lower():
            detail_msg = 'Assinatura do token inválida'
        else:
            detail_msg = 'Token inválido'

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )

def is_tokens_blacklisted(tokens: str, db: Session) -> bool:
    """Verifica se o tokens está na blacklist"""
    blacklisted = db.query(TokensBlacklist).filter(tokens == TokensBlacklist.tokens).first()
    return blacklisted is not None

def add_tokens_to_blacklist(tokens: str, user_id: int, user_role: str, expires_at: datetime, db: Session):
    """Adiciona tokens à blacklist"""
    blacklist_entry = TokensBlacklist(
        tokens=tokens,
        user_id=user_id,
        user_role=user_role,
        expires_at=expires_at
    )
    db.add(blacklist_entry)
    db.commit()


