from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.ride import RideList, RideResponse, RideRating
from app.db.database import get_db
from app.models.client import Client
from app.models.ride import Ride
from datetime import datetime
from app.auth.dependencies import get_current_user
from app.models.driver import Driver
from app.models.ride import Ride
from app.services.ride import (
    new_ride,
    get_rides_by_client,
    cancel_ride,
    start_ride,
    finish_ride,
    get_current_ride_by_client,
    rate_ride
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
    current_user = Depends(get_current_user)
):
    # Preenche client_id automaticamente, não exige vehicle_id nem driver_id
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem solicitar corrida"
        )
    ride_data = ride.model_dump()
    ride_data["client_id"] = current_user['user'].id
    ride_data.pop("vehicle_id", None)
    ride_data.pop("driver_id", None)
    ride_data["status"] = "pending"  # aguardando motorista aceitar
    created_ride = new_ride(ride_data, db)
    return {"ride": created_ride}

@router.get("/available", response_model=RideList)
def list_available_rides(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem ver corridas disponíveis"
        )
    rides = db.query(Ride).filter(Ride.status == "pending").all()
    return {"rides": rides}

@router.put("/{ride_id}/accept", response_model=RideResponse)
def accept_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Apenas motoristas podem aceitar corrida"
        )
    ride = db.query(Ride).filter(Ride.id == ride_id, Ride.status == "pending").first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Corrida não disponível para aceitação"
        )

    driver = current_user['user']
    if not driver.vehicles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Motorista não tem veículo cadastrado"
        )
    ride.driver_id = driver.id
    ride.vehicle_id = driver.vehicles[0].id
    ride.status = "accepted"  # agora sim muda status
    ride.updated_at = datetime.now()
    db.commit()
    db.refresh(ride)
    return {"ride": ride}

@router.get("/my-history", response_model=RideList)
def get_client_ride_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem ver o histórico de corridas"
        )
    rides = get_rides_by_client(current_user['user'].id, db)
    return {"rides": rides}

@router.get("/current-ride", response_model=RideResponse)
def get_current_ride(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem ver sua corrida atual"
        )
    ride = get_current_ride_by_client(current_user['user'].id, db)
    if not ride:
        raise HTTPException(status_code=404, detail="Nenhuma corrida em andamento encontrada")
    return {"ride": ride}


# Client/Driver
@router.put("/{ride_id}/cancel", response_model=RideResponse)
def cancel_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = current_user["user"].id
    role = current_user["role"]
    ride = cancel_ride(user_id, role, ride_id, db)
    return {"ride": ride}



# Driver/Motorista que inicia a corrida
@router.put("/{ride_id}/start", response_model=RideResponse)
def start_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Apenas motoristas podem iniciar corrida"
        )
    ride = start_ride(current_user['user'].id, ride_id, db)
    return {"ride": ride}


# Driver/Motorista que finaliza a corrida
@router.put("/{ride_id}/finish", response_model=RideResponse)
def finish_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Apenas motoristas podem finalizar corrida"
        )
    ride = finish_ride(current_user['user'].id, ride_id, db)
    return {"ride": ride}

@router.put("/{ride_id}/rate", response_model=RideResponse)
def rate_ride_route(
    ride_id: int,
    rating_data: RideRating,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem avaliar a corrida"
        )
    ride = rate_ride(current_user['user'].id, ride_id, rating_data.rating, db)
    return {"ride": ride}