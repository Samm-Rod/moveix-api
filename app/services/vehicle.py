from sqlalchemy.orm import Session
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleStatus
)
from app.models.vehicle import Vehicle
from fastapi import HTTPException, status
from app.models.driver import Driver


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
        license_category=vehicle_data.license_category,
        status=vehicle_data.status,
        size=vehicle_data.size
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
    # 1. Buscar veículo
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Vehicle not found'
        )
    
    # 2. Validar propriedade
    if vehicle.driver_id != driver_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to choose this vehicle'
        )
    
    # 3. Validar se já está ativo
    if vehicle.status == VehicleStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Vehicle is already active'
        )
    
    # 4. Validar se pode ser ativado
    if vehicle.status == VehicleStatus.UNDER_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Vehicle is under review and cannot be activated'
        )
    
    # 5. Desativar outros veículos do motorista (se necessário)
    db.query(Vehicle).filter(
        Vehicle.driver_id == driver_id,
        Vehicle.status == VehicleStatus.ACTIVE
    ).update({Vehicle.status: VehicleStatus.INACTIVE})
    
    # 6. Ativar o veículo
    vehicle.status = VehicleStatus.ACTIVE
    
    try:
        db.commit()
        db.refresh(vehicle)
        return vehicle
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to activate vehicle'
        )

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
