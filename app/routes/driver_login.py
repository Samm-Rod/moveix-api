from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import DriverLogin, Token
from app.services.auth_driver import authenticate_driver
from app.auth.auth_service import create_access_token

router = APIRouter(prefix='/drivers', tags=['Drivers'])

@router.post('/login', response_model=Token)
def login(driver_data: DriverLogin, db: Session = Depends(get_db)):
    driver = authenticate_driver(driver_data.email, driver_data.password, db)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": str(driver.id)})
    return {"access_token": access_token, "token_type": "bearer"}