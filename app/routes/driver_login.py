from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import Token
from app.services.auth_driver import authenticate_driver
from app.auth.auth_service import create_access_token

router = APIRouter()

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    driver = authenticate_driver(form_data.username, form_data.password, db)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    access_token = create_access_token(data={"sub": str(driver.id)})
    return {"access_token": access_token, "token_type": "bearer"}