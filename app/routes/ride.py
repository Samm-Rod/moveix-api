from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.ride import RideList
from app.db.database import get_db
from app.models.client import Client
from app.models.ride import Ride
from datetime import datetime
from app.auth.dependencies import get_current_driver
from app.models.driver import Driver
from app.auth.dependencies import get_current_client
from app.services.ride import (
    new_ride,
    get_rides_by_client,
    cancel_ride,
    start_ride,
    finish_ride
)
from app.schemas.ride import (
    RideCreate,
    RideResponse
)

router = APIRouter()


@router.post("/", response_model=RideResponse)
def create_ride(
    ride: RideCreate,
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    # Preenche client_id automaticamente, não exige vehicle_id nem driver_id
    ride_data = ride.model_dump()
    ride_data["client_id"] = current_client['client'].id
    ride_data.pop("vehicle_id", None)
    ride_data.pop("driver_id", None)
    ride_data["status"] = "pending"  # aguardando motorista aceitar
    created_ride = new_ride(ride_data, db)
    return {"ride": created_ride}

@router.get("/available", response_model=RideList)
def list_available_rides(
    db: Session = Depends(get_db),
    current_driver = Depends(get_current_driver)
):
    # Motorista vê todas as corridas pendentes
    rides = db.query(Ride).filter(Ride.status == "pending").all()
    return {"rides": rides}

@router.put("/{ride_id}/accept", response_model=RideResponse)
def accept_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_driver = Depends(get_current_driver)
):
    ride = db.query(Ride).filter(Ride.id == ride_id, Ride.status == "pending").first()
    if not ride:
        raise HTTPException(status_code=404, detail="Corrida não disponível para aceitação")
    driver = current_driver['driver']
    if not driver.vehicles:
        raise HTTPException(status_code=400, detail="Motorista não tem veículo cadastrado")
    ride.driver_id = driver.id
    ride.vehicle_id = driver.vehicles[0].id
    ride.status = "accepted"  # aguardando confirmação do cliente
    ride.updated_at = datetime.now()
    db.commit()
    db.refresh(ride)
    return {"ride": ride}

@router.put("/{ride_id}/confirm", response_model=RideResponse)
def confirm_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    ride = db.query(Ride).filter(Ride.id == ride_id, Ride.status == "accepted", Ride.client_id == current_client['client'].id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Corrida não disponível para confirmação")
    ride.status = "confirmed"  # cliente confirmou
    ride.updated_at = datetime.now()
    db.commit()
    db.refresh(ride)
    return {"ride": ride}

@router.get("/my-rides", response_model=RideList)
def list_client_rides(
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    rides = get_rides_by_client(current_client['client'].id, db)
    return {"rides": rides}


@router.get("/my-history", response_model=RideList)
def get_client_ride_history(
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    rides = get_rides_by_client(current_client['client'].id, db)
    return {"rides": rides}


@router.put("/{ride_id}/cancel", response_model=RideResponse)
def cancel_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    ride = cancel_ride(current_client['client'].id, ride_id, db)
    return {"ride": ride}


@router.put("/{ride_id}/start", response_model=RideResponse)
def start_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    ride = start_ride(current_client['client'].id, ride_id, db)
    return {"ride": ride}


@router.put("/{ride_id}/finish", response_model=RideResponse)
def finish_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_client = Depends(get_current_client)
):
    ride = finish_ride(current_client['client'].id, ride_id, db)
    return {"ride": ride}