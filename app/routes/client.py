from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.client import new_client, get_update_client, delete_client
from app.auth.dependencies import get_current_client
from app.schemas.client import (
    ClientCreate, 
    ClientUpdate,
    ClientResponse,
    ClientDeleteResponse
)
from app.schemas.client import Client as ClientSchema


router = APIRouter()

@router.post('/', response_model=ClientResponse)
def create_client(
    client: ClientCreate, 
    db: Session = Depends(get_db)
):
    created = new_client(client, db)
    return {'client': ClientSchema.model_validate(created['client'])}


# Rota privada - apenas cliente autenticado pode acessar
@router.get('/me', response_model=ClientResponse)
def get_me(
    current = Depends(get_current_client)
):
    return {'client': current['client']}


# Rota para atualizar seus próprios dados
@router.put('/me', response_model=ClientResponse)
def update_me(
    client_data: ClientUpdate,
    current = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    updated = get_update_client(current['client'].id, client_data, db)
    return {'client': updated}



# Rota para deletar sua conta
@router.delete('/me', response_model=ClientDeleteResponse)
def delete_me(
    current = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    delete_client(current['client'].id, db)
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