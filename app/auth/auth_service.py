# app/auth/auth_service.py
from datetime import timedelta, datetime
from jose import jwt, JWTError
from app.utils.config import SECRET_KEY, REFRESH_SECRET_KEY,ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from fastapi import HTTPException, status
from app.models.token import TokenBlacklist
from sqlalchemy.orm import Session

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})
    encode_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt
    
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token',
            headers={"WWW-Authenticate": "Bearer"},
        )

def is_token_blacklisted(token: str, db: Session) -> bool:
    """Verifica se o token está na blacklist"""
    blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    return blacklisted is not None

def add_token_to_blacklist(token: str, user_id: int, user_role: str, expires_at: datetime, db: Session):
    """Adiciona token à blacklist"""
    blacklist_entry = TokenBlacklist(
        token=token,
        user_id=user_id,
        user_role=user_role,
        expires_at=expires_at
    )
    db.add(blacklist_entry)
    db.commit()