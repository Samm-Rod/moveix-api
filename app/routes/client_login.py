from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import ClientLogin, Token
from app.services.auth_driver import authenticate_driver
from app.auth.auth_service import create_access_token

router = APIRouter(prefix='/clients', tags=['Clients'])


@router.post('/login', response_model=Token)
def login(client_data: ClientLogin, db: Session = Depends(get_db)):
    client = authenticate_driver(client_data.email, client_data.password, db)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": str(client.id)})
    return {"access_token": access_token, "token_type": "bearer"}