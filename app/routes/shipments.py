from fastapi import APIRouter, Depends, HTTPException, status 
from app.services.ride import confirm_ride, cancel_ride, get_current_ride_by_client, get_rides_by_client, get_rides_by_driver
from app.schemas.ride import RideList, RideResponse
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1")


""" Cliente solicita a corrida """
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RideResponse)
def book_ride(
    booking: RideResponse,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """ Cliente solicita a corrida """
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem solicitar frete"
        )
    ride_data = booking.model_dump(by_alias=True)
    ride_data["client_id"] = current_user["user"].id

    # booking.model_dump() ou booking.dict() dependendo da versão
    return confirm_ride(ride_data, db, current_user)


""" Cliente vê frete solicitado """
@router.get("/my-shipments", response_model=RideList)
def get_my_shipments(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ Cliente vê frete solicitado """
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes"
        )
    
    rides = get_rides_by_client(current_user["user"].id, db)
    return {"rides":rides}



""" Cliente vê frete atual em andamento"""
@router.get("/current", response_model=RideResponse)
def get_current_shipment(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ Cliente vê frete atual em andamento"""
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes"
        )
    ride = get_current_ride_by_client(current_user["user"].id, db)
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum frete em andamento"
        )
    return {"ride": ride}



"""Cancelar frete"""
@router.put("/{shipment_id}/cancel", response_model=RideResponse)
def cancel_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cliente cancelar frete"""
    user_id = current_user["user"].id
    role = current_user["role"]
    ride = cancel_ride(user_id, role, shipment_id, db)
    return {"ride": ride}

    