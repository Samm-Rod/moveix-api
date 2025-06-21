from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.client import Client 
from app.services.client import new_client, get_update_client, delete_client
from app.auth.dependencies import get_current_client
from app.schemas.client import (
    ClientCreate, 
    ClientUpdate,
    ClientResponse,
    ClientDeleteResponse
)


router = APIRouter(prefix='/clients',tags=['Clients'])

@router.post('/', response_model=ClientResponse)
def create_client(
    client: ClientCreate, 
    db: Session = Depends(get_db)
):
    return {'client': new_client(client, db)}  


# Rota privada - apenas cliente autenticado pode acessar
@router.get('/', response_model=ClientResponse)
def get_me(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    return {'client': current_client}


# Rota para atualizar seus próprios dados
@router.put('/me', response_model=ClientResponse)
def update_me(
    client_data: ClientUpdate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    updated = get_update_client(current_client.id, client_data, db)
    return {'client': updated}



# Rota para deletar sua conta
@router.delete('/me', response_model=ClientDeleteResponse)
def delete_me(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    delete_client(current_client.id, db)
    return {'message': 'Conta excluída com sucesso'}



