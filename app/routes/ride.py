from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.ride import Ride
from app.auth.dependencies import get_current_user
from app.services.ride import (
    calculator_ride,
    confirm_ride,
    get_list_rate,
    get_rides_by_client,
    cancel_ride,
    start_ride,
    finish_ride,
    get_current_ride_by_client,
    rate_ride,
    get_available_rides,
    accept_ride_service,
    get_rides_by_driver
)

from app.schemas.ride import (
    RideList,
    RideResponse,
    EvaluateDriver,
    RideRatingOut,
    RideQuoteResponse,
    RideResponse
)


router = APIRouter()
security = HTTPBearer()


# @router.get('/quote', response_model=RideQuoteResponse)
# async def quote(
#     origin: str = Query(..., description="Endereço de partida"),
#     destination: str = Query(..., description="Endereço de destino"),
#     db: Session = Depends(get_db),
#     current_user = Depends(security)
# ):
#     return await calculator_ride(origin, destination, db, current_user)

# Cliente confirma a corrida
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RideResponse)
def book_ride(
    booking: RideResponse,
    db: Session = Depends(get_db),
    current_user: dict = Depends(security)
):
    ride_data = booking.model_dump(by_alias=True)
    ride_data["client_id"] = current_user["user"].id

    # booking.model_dump() ou booking.dict() dependendo da versão
    return confirm_ride(ride_data, db, current_user)

@router.get("/available", response_model=RideList)
def list_available_rides(
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem ver corridas disponíveis"
        )
    rides = get_available_rides(db)
    return {"rides": rides}

@router.put("/{ride_id}/accept", response_model=RideResponse)
def accept_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Apenas motoristas podem aceitar corrida"
        )
    ride = accept_ride_service(current_user['user'], ride_id, db)
    return {"ride": ride}

@router.get("/my-rides", response_model=RideList)
def get_driver_rides(
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem ver suas corridas"
        )
    rides = get_rides_by_driver(current_user['user'].id, db)
    return {"rides": rides}

@router.get('/my_ratings', response_model=List[RideRatingOut])
def get_rate_by_driver(
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    if current_user['role'] != 'driver':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas Motoristas podem ver suas avaliações de corridas"
        )
    rides = get_list_rate(current_user['user'].id, db)
    return rides

@router.get("/my-history", response_model=RideList)
def get_client_ride_history(
    db: Session = Depends(get_db),
    current_user = Depends(security)
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
    current_user = Depends(security)
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
    current_user = Depends(security)
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
    rating_data: EvaluateDriver,
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