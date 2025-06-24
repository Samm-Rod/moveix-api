from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.vehicle import Vehicle
from app.schemas.driver import Driver 
from app.auth.dependencies import get_current_user
from app.services.vehicle import (
    create_vehicle, get_all_vehicles, update_vehicle, delete_vehicle, choose_vehicle
)
from app.schemas.vehicle import (
    VehicleCreate, VehicleList, VehicleUpdate, VehicleResponse, VehicleChoose
)

router = APIRouter()

@router.post('/', response_model=VehicleResponse)
def new_vehicle(
    vehicle: VehicleCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    created_vehicle = create_vehicle(vehicle, current_user['user'].id, db)
    return {"vehicle": created_vehicle}

@router.get('/', response_model=VehicleList)
def get_all_veh(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    vehicles = get_all_vehicles(current_user['user'], db)
    return {"vehicles": vehicles}

@router.put('/{vehicle_id}', response_model=VehicleResponse)
def edit_data_veh(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    veh_update = update_vehicle(vehicle_id, vehicle_data, current_user['user'].id, db)
    return {"vehicle": veh_update}

@router.delete('/{vehicle_id}', response_model=VehicleResponse)
def remove_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    deleted = delete_vehicle(vehicle_id, current_user['user'].id, db)
    return deleted

@router.put('/{vehicle_id}/choose', response_model=VehicleChoose)
def choose_vehicle_route(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    vehicle = choose_vehicle(vehicle_id, current_user['user'].id, db)
    return {"vehicle": vehicle}
