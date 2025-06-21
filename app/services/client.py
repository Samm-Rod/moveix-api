from app.models.client import Client
from app.schemas.client import (
    ClientCreate, ClientUpdate
)
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.utils.hashing import hash_password, verify_password
from app.auth.auth_service import create_access_token

def new_client(client_data: ClientCreate, db: Session):
    # Verifica se já existe cliente com mesmo e-mail ou CPF
    existing_email = db.query(Client).filter(Client.email == client_data.email).first()
    existing_cpf = db.query(Client).filter(Client.cpf == client_data.cpf).first()

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
        data = client_data.model_dump()
        data['hashed_password'] = hash_password(client_data.password)
        data.pop('password')  # Remove campo plaintext

        db_client = Client(**data)
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating client: {str(e)}"
        )

def get_me(current_client: Client, db: Session):
    return [current_client]

def get_all_clients(current_client: Client, db: Session):

    if not db.query(Client).filter(Client.id == current_client.id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client not found'
        )
    
    clients = db.query(Client).filter(Client == current_client).all()

    return clients


def get_client_by_id(client_id: int, db: Session):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client not found'
        )
    
    return client

def get_update_client(client_id: int, client_data: ClientUpdate, db: Session):

    client = db.query(Client).filter(Client.id == client_id).first()

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
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Client not found to Update'
        )

    db.delete(client)
    db.commit()



