# app/services/client.py
from app.models import ClientAuth, ClientMeta
from app.models.client import Client

from app.schemas.client import (
    ClientCreate, ClientUpdate
)
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.utils.hashing import hash_password
from app.auth.two_f import generate_2fa_secret, send_2fa_code, generate_2fa_code, verify_2fa_code
import random
import string

def new_client(client_data: ClientCreate, db: Session):
    # Verifica se já existe cliente com mesmo e-mail ou CPF
    existing_email = db.query(Client).filter(client_data.email == Client.email).first()
    existing_cpf = db.query(Client).filter(client_data.cpf == Client.cpf).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client already exists with this email"
        )
        
    if existing_cpf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client already exists with this CPF"
        )


    try:
        db_client = Client(
            name=client_data.name,
            email=client_data.email,
            phone=client_data.phone,
            cpf=client_data.cpf,
            address=client_data.address,
            city=client_data.city,
            state=client_data.state,
            postal_code=client_data.postal_code,
            country=client_data.country,
            auth=ClientAuth(
                hashed_password=hash_password(client_data.password),
            ),
            meta=ClientMeta()
        )
        db.add(db_client)
        db.commit()
        db.refresh(db_client)

        return db_client

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating client: {str(e)}")


def get_me(current_client: Client):
    return [current_client]

def get_all_clients(current_client: Client, db: Session):
    if not db.query(Client).filter(Client.id == current_client.id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client not found'
        )

    clients = db.query(Client).filter(current_client.id == Client.id).all()
    return clients

def get_client_by_id(client_id: int, db: Session):
    client = db.query(Client).filter(client_id == Client.id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client not found'
        )
    
    return client

def get_update_client(client_id: int, client_data: ClientUpdate, db: Session):
    client = db.query(Client).filter(client_id == Client.id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client not found to Update'
        )
    
    for field, value in client_data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client

def delete_client(client_id: int, db: Session):
    client = db.query(Client).filter(client_id == Client.id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client not found to Update'
        )

    db.delete(client)
    db.commit()

# Iniciar 2FA para login ou ação sensível
def start_2fa_for_client(client: Client, db):
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if not hasattr(client, 'two_fa_secret') or not client.two_fa_secret:
        # Gera e salva segredo se não existir
        secret = generate_2fa_secret()
        client.two_fa_secret = secret
        db.commit()
        db.refresh(client)
    else:
        secret = client.two_fa_secret
    code = generate_2fa_code(secret)
    send_2fa_code(client.email, code)
    return True

# Validar código 2FA
def validate_2fa_for_client(client: Client, code: str) -> bool:
    if not client or not hasattr(client, 'two_fa_secret') or not client.two_fa_secret:
        return False
    return verify_2fa_code(client.two_fa_secret, code)

# Iniciar fluxo de esqueci a senha
def forgot_password_client(email: str, db):
    client = db.query(Client).filter(Client.email == email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    # Gera código temporário (mock)
    code = ''.join(random.choices(string.digits, k=6))
    client.reset_code = code
    db.commit()
    db.refresh(client)
    send_2fa_code(client.email, code)
    return True

# Validar código e redefinir senha
def reset_password_client(email: str, code: str, new_password: str, db):
    client = db.query(Client).filter(Client.email == email).first()
    if not client or client.reset_code != code:
        raise HTTPException(status_code=400, detail="Código inválido")
    client.hashed_password = hash_password(new_password)
    client.reset_code = None
    db.commit()
    db.refresh(client)
    return True



