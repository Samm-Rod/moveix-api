from app.models.driver_meta import DriverMeta
from app.models.driver import Driver
from app.models.driver_auth import DriverAuth
from app.schemas.driver import DriverCreate, DriverUpdate, DriverBase
from sqlalchemy.orm import Session
from fastapi import HTTPException, status 
from app.utils.hashing import hash_password
from app.auth.two_f import generate_2fa_secret, send_2fa_code, generate_2fa_code, verify_2fa_code
import random
import string
from datetime import datetime, date
import asyncio
import logging

logger = logging.getLogger(__name__)


"""
-> Cadastrar motorista:
   - Nome completo
   - Data de nascimento
   - CPF
   - E-mail
   - Telefone
   - Nº CNH
   - Categoria CNH
   - Modelo, cor e placa do veículo
   - Cidade e Estado
"""

def new_driver_service(driver_data: DriverCreate, db: Session):
    # Checa se já existe email ou CPF
    existing_email = db.query(Driver).filter(driver_data.email == Driver.email).first()
    existing_cpf = db.query(Driver).filter(driver_data.cpf == Driver.cpf).first()



    if existing_email:
        raise HTTPException(status_code=400, detail="Driver already exists with this email")
    if existing_cpf:
        raise HTTPException(status_code=400, detail="Driver already exists with this CPF")

    try:
        # ⃣  Cria o Driver
        db_driver = Driver(
            name=driver_data.name,
            email=driver_data.email,
            birth_date=datetime.combine(driver_data.birth_date, datetime.min.time()) if isinstance(
                driver_data.birth_date, date) else driver_data.birth_date,
            phone=driver_data.phone,
            cpf=driver_data.cpf,
            address=driver_data.address,
            city=driver_data.city,
            state=driver_data.state,
            postal_code=driver_data.postal_code,
            country=driver_data.country,
            auth=DriverAuth(
                hashed_password=hash_password(driver_data.password),
                is_active=True,
                is_blocked=False
            ),
            meta=DriverMeta(
                rating=5.0
            )
        )

        db.add(db_driver)
        db.commit()
        db.refresh(db_driver)

        return db_driver

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating driver: {str(e)}")

def get_me(current_driver: Driver):
    return [current_driver]

def get_driver_by_id(driver_id: int,  db: Session):
    driver = db.query(Driver).filter(driver_id == Driver.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver not found"
        )
    return driver


def update_driver_service(driver_id: int, driver_data: DriverUpdate, db: Session):
    driver = db.query(Driver).filter(driver_id == Driver.id).first()

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver not found"
        )

    # Só atualiza os campos enviados no JSON
    for field, value in driver_data.model_dump(exclude_unset=True).items():
        if value is None:
            continue
        if isinstance(value, str) and (value.strip() == "" or value.lower() == "string"):
            continue
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)
    return driver


def delete_driver_service(driver_id: int, db: Session):
    driver = db.query(Driver).filter(driver_id == Driver.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver not found"
        )

    db.delete(driver)
    db.commit()


def start_2fa_for_driver(driver: Driver, db):
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Driver not found !'
        )
    # Corrige acesso ao valor real do campo
    secret = getattr(driver, 'two_fa_secret', None)
    if not secret:
        secret = generate_2fa_secret()
        setattr(driver, 'two_fa_secret', secret)
        db.commit()
        db.refresh(driver)
    code = generate_2fa_code(str(secret))
    asyncio.run(send_2fa_code(str(driver.email), code))
    return True


def validate_2fa_for_driver(driver: Driver, code: str) -> bool:
    secret = getattr(driver, 'two_fa_secret', None)
    if not driver or not secret:
        return False
    return verify_2fa_code(str(secret), code)

def forgot_password_driver(email: str, db):
    driver = db.query(Driver).filter(Driver.email == email).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver not found !"
        )
    code = ''.join(random.choices(string.digits, k=6))
    driver.reset_code = code
    db.commit()
    db.refresh(driver)
    asyncio.run(send_2fa_code(str(driver.email), code))
    return True

def reset_password_driver(email: str, code: str, new_password: str, db):
    driver = db.query(Driver).filter(Driver.email == email).first()
    if not driver or driver.reset_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid code'
        )
    driver.hashed_password = hash_password(new_password)
    driver.reset_code = None
    db.commit()
    db.refresh(driver)
    return True

