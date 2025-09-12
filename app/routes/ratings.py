# app/routes/ratings.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.ride import RideRatingOut, RideResponse, EvaluateDriver

from app.services.ride import rate_ride, get_list_rate


router = APIRouter(prefix="/api/v1")


"""Cliente avalia o frete/motorista"""
@router.post("/shipments/drivers/{shipment_id}", response_model=RideResponse)
def rate_shipment(
    shipment_id: int,
    rating_data: EvaluateDriver,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cliente avalia o frete/motorista"""
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem avaliar"
        )

    ride = rate_ride(current_user['user'].id, shipment_id, rating_data.rating, db)
    return {"ride": ride}


"""Cliente avalia o frete/ajudantes"""
@router.post("/shipments/helpers/{shipment_id}", response_model=RideResponse)
def rate_shipment(
    shipment_id: int,
    rating_data: EvaluateDriver,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cliente avalia o frete/ajudantes"""
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem avaliar"
        )

    ride = rate_ride(current_user['user'].id, shipment_id, rating_data.rating, db)
    return {"ride": ride}


"""Motorista vê suas avaliações recebidas"""
@router.get("/my-ratings-drivers", response_model=List[RideRatingOut])
def get_my_ratings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Motorista vê suas avaliações recebidas"""
    if current_user['role'] != 'driver':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas"
        )

    ratings = get_list_rate(current_user['user'].id, db)
    return ratings

"""Ajudante vê suas avaliações recebidas"""
@router.get("/my-ratings-helpers", response_model=List[RideRatingOut])
def get_my_ratings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ajudante vê suas avaliações recebidas"""
    if current_user['role'] != 'helper':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas ajudantes"
        )

    ratings = get_list_rate(current_user['user'].id, db)
    return ratings


"""Ver avaliações públicas de um motorista"""
@router.get("/driver/{driver_id}", response_model=List[RideRatingOut])
def get_driver_public_ratings(
    driver_id: int,
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Ver avaliações públicas de um motorista"""
    ratings = get_list_rate(driver_id, db, limit=limit, public_only=True)
    return ratings


"""Ver avaliações públicas de um ajudante"""
@router.get("/helper/{helper_id}", response_model=List[RideRatingOut])
def get_helper_public_ratings(
    helper_id: int,
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Ver avaliações públicas de um ajudante"""
    ratings = get_list_rate(helper_id, db, limit=limit, public_only=True)
    return ratings