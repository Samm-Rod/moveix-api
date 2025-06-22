from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.ride import RideList
from app.db.database import get_db
from app.models.client import Client
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
    current_client: Client = Depends(get_current_client)
):
    ride.client_id = current_client.id
    created_ride = new_ride(ride, db)
    return {"ride": created_ride}

@router.get("/my-rides", response_model=RideList)
def list_client_rides(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    rides = get_rides_by_client(current_client.id, db)
    return {"rides": rides}



@router.get("/my-history", response_model=RideList)
def get_client_ride_history(
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    rides = get_rides_by_client(current_client.id, db)
    return {"rides": rides}


@router.put("/{ride_id}/cancel", response_model=RideResponse)
def cancel_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    ride = cancel_ride(current_client.id,ride_id, db)
    return {"ride": ride}


@router.put("/{ride_id}/start", response_model=RideResponse)
def start_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    ride = start_ride(current_client.id,ride_id, db)
    return {"ride": ride}


@router.put("/{ride_id}/finish", response_model=RideResponse)
def finish_ride_route(
    ride_id: int,
    db: Session = Depends(get_db),
    current_client: Client = Depends(get_current_client)
):
    ride = finish_ride(current_client.id,ride_id, db)
    return {"ride": ride}