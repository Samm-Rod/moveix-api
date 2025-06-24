from sqlalchemy.orm import Session
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleList, VehicleRemove
)
from app.models.vehicle import Vehicle
from fastapi import HTTPException, status
from app.models.driver import Driver

"""
    -> Cadastrar novos veículos
        - Modelo
        - Placa
        - Cor 
        - Nº CNH
        - Categoria

    -> Listar meus veículos cadastrados
        - *
    
    -> Atualizar os dados de um veículo
        - *
    
    -> Removê-lo da minha lista 
        - *
    -> Trocar de veículo
        - *

"""

def create_vehicle(vehicle_data: VehicleCreate, driver_id: int, db: Session):
    existing_vehicle = db.query(Vehicle).filter(Vehicle.plate == vehicle_data.plate).first()

    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Vehicle with this plate already exists'
        )
    
    new_vehicle = Vehicle(
        driver_id=driver_id,
        model=vehicle_data.model,
        brand=vehicle_data.brand,
        plate=vehicle_data.plate,
        color=vehicle_data.color,
        license_category=vehicle_data.license_category
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle


def get_all_vehicles(current_driver: Driver, db: Session):

    if not db.query(Driver).filter(Driver.id == current_driver.id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Driver not found'
        )

    vehicles = db.query(Vehicle).filter(Vehicle.driver_id == current_driver.id).all()

    return vehicles

def choose_vehicle(vehicle_id: int, driver_id: int, db: Session):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Vehicle not found'
        )
    
    if vehicle.driver_id != driver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to choose this vehicle'
        )

    return vehicle


def update_vehicle(vehicle_id: int, vehicle_data: VehicleUpdate, driver_id: int, db: Session):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Vehicle not found'
        )
    
    if vehicle.driver_id != driver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to update this vehicle'
        )

    
    for field, value in vehicle_data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle


def delete_vehicle(vehicle_id: int, driver_id: int, db: Session):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Vehicle not found'
        )
    
    if vehicle.driver_id != driver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to delete this vehicle'
        )

    db.delete(vehicle)
    db.commit()

    return {'message': 'Vehicle removed successfully'}
