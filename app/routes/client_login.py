from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db
from app.services.auth_client import authenticate_client
from app.auth.auth_service import create_access_token
from app.schemas.auth import Token

router = APIRouter()

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client = authenticate_client(form_data.username, form_data.password, db)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": str(client.id)})
    print(f"TOKEN : {access_token}")
    return {"access_token": access_token, "token_type": "bearer"}


"""
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzUwNjMyNTkzfQ.TluxQp45Zwnr-R9H1T9gF6pXQRF5UbUXcOKGfzxobSg",
  "token_type": "bearer"
}
"""