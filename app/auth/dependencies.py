# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.auth_service import decode_token, is_token_blacklisted
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_current_user(credentials = Depends(security), db: Session = Depends(get_db)):
    """Obtém o usuário atual a partir do token"""
    try:
        # O HTTPBearer já remove o prefixo "Bearer " automaticamente
        raw_token = credentials.credentials
        
        # Remove "Bearer " extra se existir (proteção contra duplo Bearer)
        if raw_token.startswith("Bearer "):
            clean_token = raw_token.replace("Bearer ", "")
        else:
            clean_token = raw_token
        
        # Para a blacklist, vamos usar o token com prefixo Bearer
        full_token = f"Bearer {clean_token}"
        
        # Verifica se o token está na blacklist
        if is_token_blacklisted(full_token, db):
            logger.warning(f"Blacklisted token access attempt")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token foi invalidado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decodifica o token (sem o prefixo Bearer)
        payload = decode_token(clean_token)
        user_id = payload.get("sub")
        user_role = payload.get("role")
        exp = payload.get("exp")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verifica se o token não expirou
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": int(user_id),
            "role": user_role,
            "token": full_token,  # Salva o token completo com Bearer para blacklist
            "expires_at": datetime.fromtimestamp(exp) if exp else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao validar token",
            headers={"WWW-Authenticate": "Bearer"},
        )