from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.hashing import verify_password
from app.auth.auth_service import create_access_token
from app.models.client import Client
from app.models.driver import Driver
from app.schemas.auth import Token, ForgotPasswordRequest, ResetPasswordRequest, TwoFAValidateRequest
from app.services.auth import (
    get_user_by_email,
    start_2fa_for_user,
    validate_2fa_for_user,
    forgot_password_user,
    reset_password_user
)
from app.auth.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()

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
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid credentials"
    )

@router.post('/2fa/start')
async def start_2fa(request: ForgotPasswordRequest, db: Session = Depends(get_db), current_user = Depends(security)):
    user = get_user_by_email(request.email, db)
    if not current_user or user.id != current_user['user'].id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Acesso negado'
        )
    await start_2fa_for_user(user, db)
    return {'message': 'Código 2FA enviado'}

@router.post('/2fa/validate')
def validate_2fa(request: TwoFAValidateRequest, db: Session = Depends(get_db), current_user = Depends(security)):
    # Agora o e-mail vem do body do request
    user = get_user_by_email(str(request.email), db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Usuário não encontrado'
        )
    if not current_user or user.id != current_user['user'].id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Acesso negado'
        )
    valid = validate_2fa_for_user(user, request.code)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Código 2FA inválido'
        )
    return {'message': '2FA validado com sucesso'}

@router.post('/forgot-password')
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    await forgot_password_user(request.email, db)
    return {'message': 'Código de redefinição enviado para o e-mail'}

@router.post('/reset-password')
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_password_user(request.email, request.code, request.new_password, db)
    return {'message': 'Senha redefinida com sucesso'}
