from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.driver import DriverCreate, Driver, DriverUpdate, DriverResponse
from app.services.driver import (
    new_driver_service,
    get_driver_by_id,
    update_driver_service,
    delete_driver_service
)
from app.auth.dependencies import get_current_user

router = APIRouter()

# Criar motorista
@router.post('/', response_model=DriverResponse)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    driver = new_driver_service(driver, db)
    return {'driver': driver}

# Obter dados do próprio motorista
@router.get('/me', response_model=DriverResponse)
def read_current_driver(
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'driver':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Acesso permitido apenas para motoristas')
    return {'driver': current_user['user']}

# Atualizar dados do próprio motorista
@router.put('/', response_model=DriverResponse)
def update_driver(
    driver_data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'driver':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Acesso permitido apenas para motoristas')
    updated_driver = update_driver_service(current_user['user'].id, driver_data, db)
    return {'driver': updated_driver}

# Deletar conta do motorista
@router.delete('/', response_model=dict)
def delete_driver(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'driver':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Acesso permitido apenas para motoristas')
    delete_driver_service(current_user['user'].id, db)
    return {'message': 'Conta deletada com sucesso'}
