from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.hashing import verify_password
from app.auth.auth_service import create_access_token
from app.models.client import Client
from app.models.driver import Driver
from app.schemas.auth import Token

router = APIRouter()

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Primeiro tenta como cliente
    user = db.query(Client).filter(Client.email == form_data.username).first()
    if user and verify_password(form_data.password, user.hashed_password):
        return {
            "access_token": create_access_token(data={"sub": str(user.id), "role": "client"}),
            "token_type": "bearer"
        }

    # Depois tenta como driver
    user = db.query(Driver).filter(Driver.email == form_data.username).first()
    if user and verify_password(form_data.password, user.hashed_password):
        print(f"User: {user}")
        return {
            "access_token": create_access_token(data={"sub": str(user.id), "role": "driver"}),
            "token_type": "bearer"
        }
    print(f"User: {user}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
