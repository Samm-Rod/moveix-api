# app/tests/test_user_service.py

import pytest
from sqlalchemy.orm import Session
from app.models.client import Client
from app.models.driver import Driver
from app.services.auth import get_user_by_email  # ajuste o caminho se necessário

@pytest.fixture
def test_client(db: Session):
    client = Client(
        name="Test User",
        email="test_user@example.com",
        hashed_password="hashedpass"
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def test_get_user_by_email_found_as_client(db: Session, test_client: Client):
    user = get_user_by_email('test_user@example.com', db)
    assert user is not None
    assert user.email == 'test_user@example.com'
    assert isinstance(user, Client)

def test_get_user_by_email_not_found(db: Session):
    user = get_user_by_email('nao_existe@example.com', db)
    assert user is None
