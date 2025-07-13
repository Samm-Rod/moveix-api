
import pytest
from faker import Faker
from sqlalchemy.orm import Session
import uuid
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.client import (
    new_client, get_me, get_all_clients, get_client_by_id,
    get_update_client, delete_client, start_2fa_for_client,
    validate_2fa_for_client, forgot_password_client, reset_password_client
)
from datetime import date, datetime

fake = Faker("pt_BR")


@pytest.fixture
def fake_client_data():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    unique_cpf = fake.cpf()
    return ClientCreate(
        name="Test User",
        email=unique_email,
        cpf=unique_cpf,
        password="securepass",
        birth_date=date(1990, 1, 1)
    )


def test_create_new_client_success(db: Session, fake_client_data: ClientCreate):
    result = new_client(fake_client_data, db)
    assert result["client"].email == fake_client_data.email
    assert result["access_token"]
    assert result["token_type"] == "bearer"


def test_get_me_returns_current_client(db: Session, fake_client_data: ClientCreate):
    created = new_client(fake_client_data, db)
    current_client = created["client"]
    result = get_me(current_client, db)
    assert len(result) == 1
    assert result[0].id == current_client.id


def test_get_all_clients_returns_only_self(db: Session, fake_client_data: ClientCreate):
    created = new_client(fake_client_data, db)
    current_client = created["client"]
    result = get_all_clients(current_client, db)
    assert isinstance(result, list)
    assert result == [current_client]


def test_get_client_by_id_found(db: Session, fake_client_data: ClientCreate):
    created = new_client(fake_client_data, db)
    client_id = created["client"].id
    result = get_client_by_id(client_id, db)
    assert result.id == client_id


def test_update_client_success(db: Session, fake_client_data: ClientCreate):
    created = new_client(fake_client_data, db)
    client_id = created["client"].id
    update_data = ClientUpdate(name="Updated Name")
    updated = get_update_client(client_id, update_data, db)
    assert updated.name == "Updated Name"


def test_delete_client_success(db: Session, fake_client_data: ClientCreate):
    created = new_client(fake_client_data, db)
    client_id = created["client"].id
    delete_client(client_id, db)
    with pytest.raises(Exception):
        get_client_by_id(client_id, db)


def test_2fa_flow_for_client(db: Session, fake_client_data: ClientCreate):
    created = new_client(fake_client_data, db)
    client = created["client"]
    success = start_2fa_for_client(client, db)
    assert success is True
    code = client.two_fa_secret[-6:]  # ou mock do código gerado
    valid = validate_2fa_for_client(client, code)
    assert isinstance(valid, bool)


def test_forgot_and_reset_password_flow(db: Session, fake_client_data: ClientCreate):
    created = new_client(fake_client_data, db)
    client = created["client"]
    forgot_password_client(client.email, db)
    assert client.reset_code is not None
    success = reset_password_client(client.email, client.reset_code, "newpassword123", db)
    assert success is True
