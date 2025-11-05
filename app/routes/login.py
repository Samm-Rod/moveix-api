from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from app.db.database import get_db

from app.utils.hashing import verify_password
from app.auth.auth_service import create_access_tokens, create_refresh_tokens, add_tokens_to_blacklist
from app.auth.dependencies import get_current_user
from app.models.client import Client
from app.models.driver import Driver
from app.models.driver_meta import DriverMeta
from app.models.helper import Helper

from app.schemas.client import ClientCreate
from app.schemas.driver import DriverCreate
from app.schemas.helper import HelperCreate
from app.schemas.token_blacklist import TokenBlacklistCreate, TokenBlacklistResponse

from app.services.client import new_client
from app.services.driver import new_driver_service
from app.services.helper import create_helper
from app.services.token_blacklist_service import add_token_to_blacklist, is_token_blacklisted


from app.schemas.auth import (
    Tokens, ForgotPasswordRequest,
    ResetPasswordRequest, TwoFAValidateRequest,
    DriverRegisterResponse,
    ClientRegisterResponse,
    HelperRegisterResponse
)
from app.services.auth import (
    get_user_by_email,
    start_2fa_for_user,
    validate_2fa_for_user,
    forgot_password_user,
    reset_password_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")
security = HTTPBearer()

# Criar Cliente
@router.post('/register/client', response_model=ClientRegisterResponse)
def create_client(
        create_client: ClientCreate,
        db: Session = Depends(get_db)
    ):
    client = new_client(create_client, db)
    tokens = create_access_tokens({'sub': str(client.id)})
    return {
        'client_id': client.id,
        'access_tokens': tokens,
        'tokens_type': 'bearer',
        'message': 'Client successfully registered!'
    }


# Criar motorista
@router.post('/register/driver', response_model=DriverRegisterResponse)
def create_driver(
        create_driver: DriverCreate,
        db: Session = Depends(get_db)
):
    driver = new_driver_service(create_driver, db)
    tokens = create_access_tokens({'sub': str(driver.id), 'role': 'driver'})
    return {
        'driver_id': driver.id,  # O modelo espera este campo
        'access_tokens': tokens,
        'tokens_type': 'bearer',
        'message': 'Driver successfully registered!'
    }

# Criar Ajudante
@router.post('/register/helper', response_model=HelperRegisterResponse)
def new_helper(
    new_create_helper: HelperCreate,
    db: Session = Depends(get_db)
):
    helper = create_helper(new_create_helper, db)
    tokens = create_access_tokens({'sub':str(helper.id), 'role': 'helper'})
    return {
        'helper_id':helper.id,
        'access_tokens': tokens,
        'tokens_type': 'bearer',
        'message': 'Helper successfully registered !'
    }


@router.post('/login', response_model=Tokens)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_types = [
        (Client, 'client'),
        (Driver, 'driver'),
        (Helper, 'helper')
    ]
    for model, role in user_types:
        user = db.query(model).filter(model.email == form_data.username).first()

        if not user:
            continue

        # pegar o hashed_password correto
        if model is Driver:
            hashed_password = user.auth.hashed_password if user.auth else None
        elif model is Client:
            hashed_password = user.auth.hashed_password  # ou como você armazenou a senha do client
        elif model is Helper:
            hashed_password = user.auth.hashed_password
        else:
            hashed_password = None



        if hashed_password and verify_password(form_data.password, hashed_password):
            access_tokens = create_access_tokens(data={'sub': str(user.id), 'role': role})
            refresh_tokens = create_refresh_tokens(data={'sub': str(user.id), 'role': role})

            if role == "driver":
                driver_meta = db.query(DriverMeta).filter(DriverMeta.driver_id == user.id).first()
                if driver_meta:
                    driver_meta.is_online = True
                    driver_meta.is_available = True
                    driver_meta.last_updated = datetime.utcnow()
                    db.commit()

            return {
                'access_tokens': access_tokens,
                'refresh_tokens': refresh_tokens,
                'tokens_type': 'bearer'
            }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid credentials'
    )


@router.post('/logout')
def logout(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user),
        authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação não fornecido"
        )

    token = authorization.split(" ")[1]

    if current_user["role"] == "driver":
        driver_meta = db.query(DriverMeta).filter(DriverMeta.driver_id == current_user["user_id"]).first()
        if driver_meta:
            driver_meta.is_online = False
            driver_meta.is_available = False
            db.commit()

    try:
        # adiciona token na blacklist
        add_tokens_to_blacklist(
            tokens=token,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
            expires_at=current_user["expires_at"],
            db=db
        )

        return {"message": "Logout realizado com sucesso"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer logout: {str(e)}"
        )

@router.post('/2fa/start')
async def start_2fa(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        user = get_user_by_email(request.email, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Usuário não encontrado'
            )

        # Verifica se o usuário atual está tentando configurar seu próprio 2FA
        if not current_user or user.id != current_user['user'].id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Você só pode configurar 2FA para sua própria conta'
            )

        await start_2fa_for_user(user, db)
        return {
            'message': 'Código 2FA enviado com sucesso',
            'email': user.email
        }
    except Exception as e:
        logger.error(f"Erro ao iniciar 2FA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro ao iniciar 2FA: {str(e)}'
        )

@router.post('/2fa/validate')
def validate_2fa(request: TwoFAValidateRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
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
    logger.warning(f"CÓDIGO DE VERIFICAÇÃO : 🔑 {valid}")
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
