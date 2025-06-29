from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate
from sqlalchemy.orm import Session
from fastapi import HTTPException, status 
from app.utils.hashing import hash_password
from app.auth.two_f import generate_2fa_secret, send_2fa_code, generate_2fa_code, verify_2fa_code
import random
import string

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
    existing_email = db.query(Driver).filter(Driver.email == driver_data.email).first()
    existing_cpf = db.query(Driver).filter(Driver.cpf == driver_data.cpf).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Driver already exists with this email"
        )
    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Driver already exists with this CPF"
        )

    try:
        data = driver_data.model_dump()
        data['hashed_password'] = hash_password(driver_data.password)
        data.pop('password')
        # Remove campos que não existem no modelo Driver
        for field in ['car_model', 'car_plate', 'car_color', 'driver_license', 'license_category']:
            data.pop(field, None)

        db_driver = Driver(**data)
        db.add(db_driver)
        db.commit()
        db.refresh(db_driver)
        return db_driver
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error creating driver: {str(e)}"
        )
    

def get_driver_by_id(driver_id: int,  db: Session):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver not found"
        )
    return driver
    

def update_driver_service(driver_id: int, driver_data: DriverUpdate, db: Session):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver not found"
        )

    for field, value in driver_data.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)
    return driver


def delete_driver_service(driver_id: int, db: Session):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Driver not found"
        )

    db.delete(driver)
    db.commit()


def start_2fa_for_driver(driver: Driver, db):
    if not driver:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    if not hasattr(driver, 'two_fa_secret') or not driver.two_fa_secret:
        secret = generate_2fa_secret()
        driver.two_fa_secret = secret
        db.commit()
        db.refresh(driver)
    else:
        secret = driver.two_fa_secret
    code = generate_2fa_code(secret)
    send_2fa_code(driver.email, code)
    return True

def validate_2fa_for_driver(driver: Driver, code: str) -> bool:
    if not driver or not hasattr(driver, 'two_fa_secret') or not driver.two_fa_secret:
        return False
    return verify_2fa_code(driver.two_fa_secret, code)

def forgot_password_driver(email: str, db):
    driver = db.query(Driver).filter(Driver.email == email).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    code = ''.join(random.choices(string.digits, k=6))
    driver.reset_code = code
    db.commit()
    db.refresh(driver)
    send_2fa_code(driver.email, code)
    return True

def reset_password_driver(email: str, code: str, new_password: str, db):
    driver = db.query(Driver).filter(Driver.email == email).first()
    if not driver or driver.reset_code != code:
        raise HTTPException(status_code=400, detail="Código inválido")
    driver.hashed_password = hash_password(new_password)
    driver.reset_code = None
    db.commit()
    db.refresh(driver)
    return True

