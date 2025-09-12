from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 
from app.db.database import get_db
from app.schemas.auth import tokens
from app.services.auth_helper import authenticate_helper
from app.auth.auth_service import create_access_tokens
import logging
import sys

# Configuração detalhada do logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Formato detalhado para os logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Adiciona o handler ao logger
if not logger.handlers:
    logger.addHandler(console_handler)

router = APIRouter()

@router.post('/login', response_model=tokens)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.debug("="*50)
    logger.debug("INICIANDO TENTATIVA DE LOGIN DE HELPER")
    logger.debug(f"Email recebido: {form_data.username}")
    
    try:
        # Tenta autenticar o helper
        helper = authenticate_helper(form_data.username, form_data.password, db)
        
        # Log do resultado da autenticação
        if helper:
            logger.info(f"Helper autenticado com sucesso: ID={helper.id}, Email={helper.email}")
            access_tokens = create_access_tokens(data={'sub':str(helper.id), 'role': 'helper'})
            logger.debug("tokens criado com sucesso")
            return {'access_tokens': access_tokens, 'tokens_type': 'bearer'}
        else:
            logger.warning(f"Falha na autenticação para o email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid credentials'
            )
    except Exception as e:
        logger.error(f"Erro durante autenticação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication error'
        )
    finally:
        logger.debug("="*50)