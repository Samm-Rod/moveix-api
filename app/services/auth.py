# app/services/auth.py
from app.models.client import Client
from app.models.driver import Driver
from app.models.helper import Helper
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.utils.hashing import hash_password
from app.auth.two_f import generate_2fa_secret, send_2fa_code, generate_2fa_code, verify_2fa_code
import random
import string
import logging

logger = logging.getLogger(__name__)

def get_user_by_email(email: str, db: Session):
    # Garante que o email é string (caso venha como EmailStr do Pydantic)
    email = str(email)
    user = db.query(Client).filter(Client.email == email).first()
    if not user:
        user = db.query(Driver).filter(Driver.email == email).first()
    if not user:
        user = db.query(Helper).filter(Helper.email == email).first()

    logger.warning(f"USER 👤: {user}")
    return user

async def start_2fa_for_user(user, db: Session):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )

    # Verifica se o secret existe no relacionamento auth
    if not user.auth.two_fa_secret:
        secret = generate_2fa_secret()
        user.auth.two_fa_secret = secret
        db.commit()
        db.refresh(user)
    else:
        secret = user.auth.two_fa_secret

    code = generate_2fa_code(secret)
    await send_2fa_code(user.email, code)
    return True


def validate_2fa_for_user(user, code: str) -> bool:
    if not user or not user.auth or not user.auth.two_fa_secret:
        return False
    return verify_2fa_code(user.auth.two_fa_secret, code)

async def forgot_password_user(email: str, db: Session):
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )
    
    code = ''.join(random.choices(string.digits, k=6))
    user.reset_code = code
    db.commit()
    db.refresh(user)
    await send_2fa_code(user.email, code)
    return True

def reset_password_user(email: str, code: str, new_password: str, db: Session):
    user = get_user_by_email(email, db)
    if not user or user.reset_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Código inválido'
        )

    user.hashed_password = hash_password(new_password)
    user.reset_code = None
    db.commit()
    db.refresh(user)
    return True
