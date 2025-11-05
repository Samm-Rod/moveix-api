
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.driver import DriverUpdate, DriverResponse, DriverProfile
from app.auth.dependencies import get_current_user
from app.schemas.freight import FreightList, FreightResponse
from app.services.driver import (
    update_driver_service,
    delete_driver_service,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

# Obter dados do próprio motorista
@router.get('/profile', response_model=DriverProfile)
def get_profile(current_user=Depends(get_current_user)):
    if current_user['role'] != 'driver':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access permitted only for drivers'
        )

    driver = current_user['user']

    # Retornando apenas os campos seguros
    return DriverProfile(
        id=driver.id,
        name=driver.name,
        email=driver.email,
        phone=driver.phone,
        rating=driver.meta.rating,
        is_active=driver.auth.is_active,
        vehicle_plate=driver.vehicle.plate if hasattr(driver, 'vehicle') and driver.vehicle else None,
        created_at=driver.meta.created_at,
        updated_at=driver.meta.updated_at
    )


# Atualizar dados do próprio motorista
@router.patch('/', response_model=DriverResponse)
def update_driver(
    driver_data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'driver':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Access permitted only for drivers'
        )
    updated_driver = update_driver_service(current_user['user'].id, driver_data, db)
    return updated_driver

# Deletar conta do motorista
@router.delete('/', response_model=dict)
def delete_driver(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user['role'] != 'driver':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Access permitted only for drivers'
        )
    delete_driver_service(current_user['user'].id, db)
    return {'message': 'Account deleted successfully'}



