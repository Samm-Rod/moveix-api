# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from app.db.database import get_db
# from app.schemas.auth import Tokens
# from app.services.auth_driver import authenticate_driver
# from app.auth.auth_service import create_access_tokens
#
# router = APIRouter()
#
# @router.post('/login', response_model=Tokens)
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     driver = authenticate_driver(form_data.username, form_data.password, db)
#     if not driver:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials"
#         )
#     access_tokens = create_access_tokens(data={"sub": str(driver.id), "role": "driver"})
#     return {"access_tokens": access_tokens, "tokens_type": "bearer"}