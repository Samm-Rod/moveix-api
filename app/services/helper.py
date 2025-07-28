from sqlalchemy.orm import Session
from fastapi import HTTPException, status 
from app.utils.hashing import hash_password
from app.auth.two_f import generate_2fa_secret, send_2fa_code, generate_2fa_code, verify_2fa_code
import random
import string
from datetime import datetime, date
import asyncio
from app.schemas.helper import HelperCreate, HelperList, HelperUpdate, HelperDeleteResponse
from app.models.helper import Helper


# Criar a service do Ajudante/Helper

def create_helper(helper_data: HelperCreate, db: Session):
    existing_email = db.query(Helper).filter(Helper.email == helper_data.email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Helper already exists with this email"
        )


    try:
        data = helper_data.model_dump()
        data['hashed_password'] = hash_password(helper_data.password)
        data.pop('password')

        if isinstance(data.get('birth_date'), date) and not isinstance(data.get('birth_date'), datetime):
            data['birth_date'] = datetime.combine(data['birth_date'], datetime.min.time())

        if 'created_at' not in data:
            data['created_at'] = datetime.now()
        if 'updated_at' not in data:
            data['updated_at'] = datetime.now()
        if 'is_active' not in data:
            data['is_active'] = True
        if 'is_blocked' not in data:
            data['is_blocked'] = False
        if 'rating' not in data:
            data['rating'] = 5.0

        db_helper = Helper(**data)
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
    helper = db.query(Helper).filter(Helper.id == helper_data.id).first()

    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Helpers not found !'
        )
    
    return helper

def update_profile(helper_data: HelperUpdate, db: Session):
    helper = db.query(Helper).filter(Helper.cpf == helper_data.cpf or Helper.email == helper_data.email).first()

    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Helper not found !'
        )
    
    for field, value, in helper_data.model_dump(exclude_unset=True).items():
        setattr(helper, field, value)

    db.commit()
    db.refresh(helper)

    return helper

def delete_account(helper_id: int, db: Session):    
    helper = db.query(Helper).filer(Helper.id == helper_id).first()
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
    secret = getattr(helper, 'two_fa_secret', None)
    if not secret: 
        secret = generate_2fa_secret()
        setattr(helper, 'two_fa_secret', secret)
        db.commit()
        db.refresh(helper)
    code = generate_2fa_code(str(secret))
    asyncio.run(send_2fa_code(str(helper.email), code))

    return True


def validate_2fa_for_helper(helper: Helper, code: str) -> str:
    secret = getattr(helper, 'two_fa_secret', None)
    if not helper or not secret:
        return False
    return verify_2fa_code(str(secret), code)

def forgot_password_helper(email: str, db):
    helper = db.query(Helper).filter(Helper.email == email).first()
    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Helper not found !"
        )
    
    code = ''.join(random.choices(string.digits, k=6))
    helper.reset_code = code
    db.commit()
    db.refresh(helper)
    asyncio.run(send_2fa_code(str(helper.email), code))
    return True

def reset_password_helper(email: str, code: str, new_password: str, db):
    helper = db.query(Helper).filter(Helper.email == email).first()
    if not helper or helper.reset_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid code'
        )

    helper.hashed_password = hash_password(new_password)
    helper.reset_code = None
    db.commit()
    db.refresh(helper)
    return True







