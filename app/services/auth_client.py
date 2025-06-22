from sqlalchemy.orm import Session 
from app.models.client import Client
from app.utils.hashing import verify_password

def authenticate_client(email: str, password: str, db: Session):
    client = db.query(Client).filter(Client.email == email).first()
    if not client:
        return None
    if not verify_password(password, client.hashed_password):
        return None
    
    print(f"Client: {client}")
    return client

    # app/services/auth_client.py