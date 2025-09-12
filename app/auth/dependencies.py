# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.auth_service import decode_tokens, is_tokens_blacklisted
from datetime import datetime
import logging

from app.models.client import Client
from app.models.driver import Driver
from app.models.helper import Helper

logger = logging.getLogger(__name__)
security = HTTPBearer()


def get_current_user(credentials = Depends(security), db: Session = Depends(get_db)):
    """Obtém o usuário atual a partir do tokens"""
    try:
        raw_tokens = credentials.credentials
        logger.debug(f"[AUTH DEBUG] Raw token header received: '{raw_tokens}'")

        # Normalize and clean the Authorization header.
        # Remove surrounding quotes/whitespace, then strip any repeated
        # 'Bearer ' prefix (case-insensitive), e.g. handle 'Bearer bearer <token>'.
        token_str = raw_tokens.strip().strip('"').strip("'")
        logger.debug(f"[AUTH DEBUG] After stripping quotes: '{token_str}'")
        
        # Remove any number of leading 'bearer ' prefixes (case-insensitive)
        original_token = token_str
        while token_str.lower().startswith("bearer "):
            token_str = token_str.split(" ", 1)[1].strip()
        
        if original_token != token_str:
            logger.debug(f"[AUTH DEBUG] Removed Bearer prefix(es). Before: '{original_token}' After: '{token_str}'")

        clean_tokens = token_str
        logger.debug(f"[AUTH DEBUG] Final clean token: '{clean_tokens[:30]}...'")

        full_tokens = f"Bearer {clean_tokens}"
        logger.debug(f"Using token for blacklist check: {full_tokens[:60]}...")

        if is_tokens_blacklisted(full_tokens, db):
            logger.warning("Blacklisted token access attempt")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token foi invalidado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = decode_tokens(clean_tokens)
        logger.info(f"🔐 Token decodificado: {payload}")
        user_id = payload.get("sub")
        user_role = payload.get("role")
        exp = payload.get("exp")
        
        logger.info(f"👤 ID do usuário: {user_id}, Role: {user_role}, Expira em: {exp}")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Normalize and check expiration (accept int timestamp, string, or datetime)
        exp_dt = None
        try:
            if exp is None:
                exp_dt = None
            elif isinstance(exp, (int, float)):
                exp_dt = datetime.fromtimestamp(exp)
            elif isinstance(exp, str):
                # try parse as int timestamp first, then ISO format
                try:
                    exp_dt = datetime.fromtimestamp(int(exp))
                except Exception:
                    try:
                        exp_dt = datetime.fromisoformat(exp)
                    except Exception:
                        exp_dt = None
            elif isinstance(exp, datetime):
                exp_dt = exp
            else:
                # unexpected type - attempt to coerce
                try:
                    exp_dt = datetime.fromtimestamp(int(exp))
                except Exception:
                    exp_dt = None
        except Exception as _e:
            logger.warning(f"Could not parse exp claim: {exp} -> {_e}")
            exp_dt = None

        if exp_dt and exp_dt < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Resolve user object by role
        user_obj = None
        if user_role is None:
            logger.warning(f"⚠️ Token sem role para user_id {user_id}. Tentando encontrar usuário...")
            # Se não tiver role, tenta encontrar o usuário em todas as tabelas
            user_obj = (
                db.query(Client).filter(Client.id == int(user_id)).first() or
                db.query(Driver).filter(Driver.id == int(user_id)).first() or
                db.query(Helper).filter(Helper.id == int(user_id)).first()
            )
            if user_obj:
                # Infere a role baseado no tipo do objeto encontrado
                if isinstance(user_obj, Client):
                    user_role = 'client'
                elif isinstance(user_obj, Driver):
                    user_role = 'driver'
                elif isinstance(user_obj, Helper):
                    user_role = 'helper'
        else:
            # Se tiver role, busca diretamente na tabela correta
            if user_role == 'client':
                user_obj = db.query(Client).filter(Client.id == int(user_id)).first()
            elif user_role == 'driver':
                user_obj = db.query(Driver).filter(Driver.id == int(user_id)).first()
            elif user_role == 'helper':
                user_obj = db.query(Helper).filter(Helper.id == int(user_id)).first()

        if not user_obj:
            logger.warning(f"User object not found for id {user_id} role {user_role}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": int(user_id),
            "role": user_role,
            "tokens": full_tokens,
            "token": full_tokens,  # compatibility
            "expires_at": datetime.fromtimestamp(exp) if exp else None,
            "user": user_obj
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





