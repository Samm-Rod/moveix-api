# app/tests/conftest.py
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from fastapi import FastAPI
from app.db.database import Base, get_db
from app.routes import client, driver, login, ride, vehicle, locations, payments, helper

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar aplicação de teste
def create_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(client.router, prefix='/clients', tags=['Clients'])
    test_app.include_router(driver.router, prefix='/drivers', tags=['Drivers'])
    test_app.include_router(login.router, prefix='/auth', tags=['Auth'])
    test_app.include_router(ride.router, prefix='/ride', tags=['Rides'])
    test_app.include_router(vehicle.router, prefix='/vehicles', tags=['Vehicles'])
    test_app.include_router(locations.router, prefix='/maps', tags=['Maps'])
    test_app.include_router(payments.router, prefix='/payments', tags=['Payments'])
    test_app.include_router(helper.router, prefix='/helpers', tags=['Helpers'])
    return test_app

# Instância global do app para testes
test_app = create_test_app()

# Dependência do banco de dados para testes
def get_test_db() -> Generator[Session, None, None]:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_test_db():
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    yield
    # Dropar tabelas
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Substituir a dependência do banco de dados
    test_app.dependency_overrides[get_db] = lambda: session
    
    yield session
    
    # Limpar após os testes
    session.close()
    transaction.rollback()
    connection.close()
    test_app.dependency_overrides.clear()

@pytest.fixture
def client(db) -> Generator[TestClient, None, None]:
    def _get_test_db():
        try:
            yield db
        finally:
            pass

    # Sobrescrever a dependência do banco de dados
    test_app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(test_app) as test_client:
        yield test_client

# Importar modelos
import app.models.client
import app.models.driver
import app.models.ride
import app.models.vehicle
import app.models.payments
import app.models.locations

# SQLite in-memory
DATABASE_URL = "sqlite://"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()

def get_test_db():
    """Função para fornecer sessão do banco de dados de teste"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configura o ambiente de teste"""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["JWT_SECRET"] = "test-secret-key"
    yield
    # Limpar variáveis de ambiente após os testes
    os.environ.pop("ENVIRONMENT", None)
    os.environ.pop("JWT_SECRET", None)

@pytest.fixture
def db():
    """Fixture que fornece uma sessão do banco de dados de teste"""
    Base.metadata.create_all(bind=engine)  # Criar tabelas
    
    # Sobrescrever a dependência do banco de dados
    app.dependency_overrides[get_db] = get_test_db
    
    # Fornecer uma sessão de teste
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)  # Limpar tabelas
        app.dependency_overrides.clear()

@pytest.fixture
def client(db):
    """Fixture que fornece um cliente de teste"""
    with TestClient(app) as test_client:
        yield test_client