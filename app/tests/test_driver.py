import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import date
from app.services.driver import (
    new_driver_service,
    get_driver_by_id,
    update_driver_service,
    delete_driver_service,
    start_2fa_for_driver,
    validate_2fa_for_driver,
    forgot_password_driver,
    reset_password_driver,
)
from app.schemas.driver import DriverCreate, DriverUpdate
from app.models.driver import Driver
from app.utils.hashing import hash_password
from app.auth.two_f import generate_2fa_code

def sample_driver_data(email: str | None = None, cpf: str | None = None) -> DriverCreate:
    # Gera dados únicos se não fornecidos
    if email is None:
        email = f"motorista_{uuid.uuid4().hex[:8]}@example.com"
    if cpf is None:
        cpf = f"{uuid.uuid4().hex[:11]}"
    
    return DriverCreate(
        name="João Freteiro",
        email=email,
        password="123456",
        birth_date=date(1990, 1, 1),
        phone="61999999999",
        cpf=cpf,
        address="Rua XPTO, 123",
        postal_code="70000000",
        city="Brasília",
        state="DF",
        country="Brasil",
        has_helpers=False,
        helper_price=None,
        car_model="Toyota Corolla",
        car_plate="ABC1234",
        car_color="Prata",
        driver_license="123456789",
        license_category="B"
    )

def test_create_new_driver_success(db: Session):
    data = sample_driver_data()
    driver = new_driver_service(data, db)
    assert driver.id is not None  # type: ignore
    assert driver.email == data.email  # type: ignore
    assert driver.name == data.name  # type: ignore
    assert driver.hashed_password != data.password  # type: ignore

def test_create_driver_duplicate_email_fails(db: Session):
    # Cria primeiro driver com email específico
    data = sample_driver_data(email="teste@email.com", cpf="11111111111")
    new_driver_service(data, db)
    # Tenta criar segundo driver com mesmo email
    with pytest.raises(HTTPException) as exc:
        new_driver_service(sample_driver_data(email="teste@email.com", cpf="22222222222"), db)
    assert exc.value.status_code == 400
    assert "email" in exc.value.detail.lower()

def test_create_driver_duplicate_cpf_fails(db: Session):
    # Cria primeiro driver com CPF específico
    data = sample_driver_data(email="teste1@email.com", cpf="11111111111")
    new_driver_service(data, db)
    # Tenta criar segundo driver com mesmo CPF
    with pytest.raises(HTTPException) as exc:
        new_driver_service(sample_driver_data(email="teste2@email.com", cpf="11111111111"), db)
    assert exc.value.status_code == 400
    assert "cpf" in exc.value.detail.lower()

def test_get_driver_by_id_success(db: Session):
    data = sample_driver_data()
    driver = new_driver_service(data, db)
    fetched = get_driver_by_id(driver.id, db)  # type: ignore
    assert fetched.id == driver.id  # type: ignore
    assert fetched.email == driver.email  # type: ignore

def test_get_driver_by_id_not_found(db: Session):
    with pytest.raises(HTTPException) as exc:
        get_driver_by_id(9999, db)
    assert exc.value.status_code == 404

def test_update_driver_success(db: Session):
    data = sample_driver_data()
    driver = new_driver_service(data, db)
    update_data = DriverUpdate(name="Novo Nome")
    updated = update_driver_service(driver.id, update_data, db)  # type: ignore
    assert updated.name == "Novo Nome"  # type: ignore

def test_delete_driver_success(db: Session):
    data = sample_driver_data()
    driver = new_driver_service(data, db)
    delete_driver_service(driver.id, db)  # type: ignore
    with pytest.raises(HTTPException):
        get_driver_by_id(driver.id, db)  # type: ignore

def test_2fa_flow_for_driver(db: Session):
    data = sample_driver_data()
    driver = new_driver_service(data, db)
    success = start_2fa_for_driver(driver, db)
    assert success is True
    code = generate_2fa_code(driver.two_fa_secret)  # type: ignore
    assert validate_2fa_for_driver(driver, code) is True  # type: ignore

def test_forgot_and_reset_password_flow_for_driver(db: Session):
    data = sample_driver_data()
    driver = new_driver_service(data, db)
    forgot = forgot_password_driver(driver.email, db)  # type: ignore
    assert forgot is True
    reset = reset_password_driver(driver.email, driver.reset_code, "novasenha123", db)  # type: ignore
    assert reset is True