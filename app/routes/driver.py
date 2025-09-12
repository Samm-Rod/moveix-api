
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.driver import DriverUpdate, DriverResponse, DriverResponseBase, DriverProfile
from app.auth.dependencies import get_current_user
from app.schemas.ride import RideList, RideResponse
from app.services.driver import (
    update_driver_service,
    delete_driver_service,
)

import logging

from app.services.ride import accept_ride_service, cancel_ride, finish_ride, get_available_rides

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")
security = HTTPBearer()

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


""" Motorista vê fretes disponíveis na região """
@router.get("/available-shipments", response_model=RideList)
def list_available_shipments(
    radius_km: int = Query(50, description="Raio de busca em KM"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas"
            )
    
    rides = get_available_rides(db, radius_km, current_user['user'])
    return {"rides": rides}



"""Motorista aceita um frete"""
@router.post("/shipments/{shipment}/accept", response_model=RideResponse)
def accept_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas"
        )
    ride = accept_ride_service(current_user["user"], shipment_id, db)
    return {"ride": ride}


"""Motorista finaliza o frete"""
@router.put("/shipments/{shipment_id}/finish", response_model=RideResponse)
def finish_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas"
        )
    
    ride = finish_ride(current_user["user"].id, shipment_id, db)
    return {"ride": ride}

"""Cancelar frete"""
@router.put("/{shipment_id}/cancel", response_model=RideResponse)
def cancel_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = current_user["user"].id
    role = current_user["role"]
    ride = cancel_ride(user_id, role, shipment_id, db)
    return {"ride": ride}