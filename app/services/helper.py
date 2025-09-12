
from sqlalchemy.orm import Session
from fastapi import HTTPException, status 
from app.utils.hashing import hash_password
from app.auth.two_f import send_2fa_code, verify_2fa_code
import random
import string
from datetime import datetime
import asyncio

from app.schemas import HelperCreate, HelperList, HelperUpdate
from app.models import Helper, HelperMeta, HelperAuth


# Criar a service do Ajudante/Helper
def create_helper(helper_data: HelperCreate, db: Session):
    existing_email = db.query(Helper).filter(helper_data.email == Helper.email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Helper already exists with this email"
        )

    try:
        db_helper = Helper(
            name=helper_data.name,
            email=helper_data.email,
            birth_date=helper_data.birth_date,
            phone=helper_data.phone,
            cpf=helper_data.cpf,
            address=helper_data.address,
            postal_code=helper_data.postal_code,
            country=helper_data.country,
            city=helper_data.city,
            state=helper_data.state,
            auth=HelperAuth(
                hashed_password=hash_password(helper_data.password),
                is_active=True,
                is_blocked=False
            ),
            meta=HelperMeta(
                rating=5.0
            )
        )

        db.add(db_helper)
        db.commit()
        db.refresh(db_helper)

        return db_helper

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating helper: {str(e)}"
        )

def get_profile(helper_data: HelperList, db: Session):
    helper = db.query(Helper).filter(helper_data.id == Helper.id).first()

    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Helpers not found !'
        )
    
    return helper

def update_profile(helper_id: int, helper_data: HelperUpdate, db: Session):
    helper = db.query(Helper).filter(Helper.id == helper_id).first()
    helper_meta = db.query(HelperMeta).filter(HelperMeta.helper_id == helper_id).first()

    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Helper not found with ID: {helper_id}!'
        )

    # Atualiza os campos enviados
    for field, value in helper_data.model_dump(exclude_unset=True).items():
        setattr(helper, field, value)

    helper_meta.updated_at = datetime.now()
    db.commit()
    db.refresh(helper)
    db.refresh(helper_meta)

    return {
        **helper.__dict__,
        "created_at": helper_meta.created_at,
        "updated_at": helper_meta.updated_at,
    }

def delete_account(helper_id: int, db: Session):    
    helper = db.query(Helper).filter(helper_id == Helper.id).first()
    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Helper not found !'
        )
    db.delete(helper)
    db.commit()

def start_2fa_for_helper(helper: Helper, db):
    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Helper not found !'
        )

def validate_2fa_for_helper(helper: Helper, code: str) -> bool:
    secret = getattr(helper, 'two_fa_secret', None)
    if not helper or not secret:
        return False
    return verify_2fa_code(str(secret), code)

def forgot_password_helper(email: str, db):
    helper = db.query(Helper).filter(Helper.email == email).first()

    helper_auth = HelperAuth()

    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Helper not found !"
        )
    
    code = ''.join(random.choices(string.digits, k=6))
    helper_auth.reset_code = code

    db.commit()
    db.refresh(helper)
    asyncio.run(send_2fa_code(str(helper.email), code))
    return True

def reset_password_helper(email: str, code: str, new_password: str, db):
    helper = db.query(Helper).filter(Helper.email == email).first()

    helper_auth = HelperAuth()

    if not helper or helper_auth.reset_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid code'
        )

    helper_auth.hashed_password = hash_password(new_password)
    helper_auth.reset_code = None
    db.commit()
    db.refresh(helper)
    return True







