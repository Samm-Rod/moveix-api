from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.auth_service import create_access_tokens
from app.auth.dependencies import get_current_user
import logging
from app.services.client import (
    get_update_client, 
    delete_client
)
from app.schemas.client import (
    ClientProfile,
    ClientUpdate,
    ClientDeleteResponse
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



router = APIRouter(prefix="/api/v1")
security = HTTPBearer()

# Rota privada - apenas cliente autenticado pode acessar
@router.get('/me', response_model=ClientProfile)
def get_me(
    current_user = Depends(get_current_user)
):
    logger.info(f"🔍 Dados do current_user: {current_user}")
    logger.info(f"🔑 Tipo do current_user: {type(current_user)}")
    if current_user['role'] != 'client':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Acesso permitido apenas para clientes'
            )
    
    # Return the client object directly
    return current_user['user']


# Rota para atualizar seus próprios dados
@router.patch('/me', response_model=ClientProfile)
def update_me(
    client_data: ClientUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"current_user type: {type(current_user)}")
    print(f"current_user content: {current_user}")
    if current_user['role'] != 'client':
        print(f"current_user type: {type(current_user)}")
        print(f"current_user content: {current_user}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Acesso permitido apenas para clientes'
            )
    updated = get_update_client(current_user['user'].id, client_data, db)
    return updated


# Rota para deletar sua conta
@router.delete('/me', response_model=ClientDeleteResponse)
def delete_me(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info('INICIANDO A REMOÇÃO DO CLIENT !')
    if current_user['role'] != 'client':
        raise HTTPException(
            logger.warning('DEU ERRO AQUI !'),
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Acesso permitido apenas para clientes'
            )
    
    delete_client(current_user['user'].id, db)
    logger.info('SUCESSO !'),
    return {'message': 'Conta excluída com sucesso'}


# {
#   "client": {
#     "name": "José",
#     "email": "jose@gmail.com",
#     "phone": "6666-6666",
#     "cpf": "66666666666",
#     "address": "rua6",
#     "city": "Brasília",
#     "state": "DF",
#     "postal_code": "66666666",
#     "country": "Brazil",
#     "id": 10,
#     "created_at": "2025-06-22T00:48:23.753794",
#     "updated_at": "2025-06-22T00:48:23.753816"
#   },
#   "role": "client"
# }