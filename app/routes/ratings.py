# app/routes/ratings.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.rating import FreightRating, FreightRatingOut
from app.services.rating import RatingService

router = APIRouter(prefix="/api/v1/ratings")

@router.post("/freight/{freight_id}", response_model=FreightRatingOut)
async def rate_freight(
    freight_id: int,
    rating_data: FreightRating,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Avalia um frete concluído.
    Pode ser usado para avaliar motorista ou ajudantes.
    """
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem avaliar"
        )

    try:
        rating_service = RatingService(db)
        return await rating_service.rate_freight(
            client_id=current_user['user'].id,
            freight_id=freight_id,
            rating_data=rating_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao avaliar frete")

@router.get("/freight/{freight_id}", response_model=List[FreightRatingOut])
async def get_freight_ratings(
    freight_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém as avaliações de um frete específico
    """
    try:
        rating_service = RatingService(db)
        return await rating_service.get_freight_ratings(freight_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao buscar avaliações")

"""Motorista vê suas avaliações recebidas"""
@router.get("/my-ratings", response_model=List[FreightRatingOut])
async def get_my_ratings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Usuário (motorista ou ajudante) vê suas avaliações recebidas"""
    if current_user['role'] not in ['driver', 'helper']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para motoristas e ajudantes"
        )

    rating_service = RatingService(db)
    return await rating_service.get_user_ratings(
        user_id=current_user['user'].id,
        user_type=current_user['role']
    )

"""Ver avaliações públicas de um motorista"""
@router.get("/driver/{driver_id}", response_model=List[FreightRatingOut])
async def get_driver_public_ratings(
    driver_id: int,
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Ver avaliações públicas de um motorista"""
    rating_service = RatingService(db)
    return await rating_service.get_user_ratings(
        user_id=driver_id,
        user_type="driver",
        limit=limit,
        public_only=True
    )

"""Ver avaliações públicas de um ajudante"""
@router.get("/helper/{helper_id}", response_model=List[FreightRatingOut])
async def get_helper_public_ratings(
    helper_id: int,
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Ver avaliações públicas de um ajudante"""
    rating_service = RatingService(db)
    return await rating_service.get_user_ratings(
        user_id=helper_id,
        user_type="helper",
        limit=limit,
        public_only=True
    )