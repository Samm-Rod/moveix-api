from fastapi import HTTPException, APIRouter
from app.schemas.trip_request import RequestRide, RequestGetById, UpdateRide, RequestCanceled
from app.auth.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.ride_request import RideRequest
from app.models.request import Request

router = APIRouter(prefix="/api/v1")

@router.post("/new_request", response_model=RequestGetById)
def create_new_request(
        request_data: RequestRide,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):

    if current_user['role'] != 'client':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem solicitar"
        )

    # Criar request
    service = RideRequest(db)
    new_request = service.create_request(
        client_id=current_user['user'].id,
        request_data=request_data
    )

    return new_request


# Visualizar request por id
@router.get("/{request_id}", response_model=RequestRide)
def view_ride(
    request_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = RideRequest(db)
    request = service.view_my_request(request_id)
    # opcional: verificar se o request pertence ao user
    if current_user["role"] == "client" and request.client_id != current_user["user"].id:
        raise HTTPException(status_code=403, detail="Não autorizado")
    return request


# Atualizar request
@router.patch("/{request_id}", response_model=RequestRide)
def update_ride(
    request_id: int,
    request_data: UpdateRide,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user['role'] != 'client':
        raise HTTPException(status_code=403, detail="Acesso negado")
    service = RideRequest(db)
    updated_request = service.update_request(request_id, request_data)
    return updated_request


# Cancelar request
@router.delete("/{request_id}", response_model=RequestCanceled)
def cancel_ride(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user['role'] != 'client':
        raise HTTPException(status_code=403, detail="Acesso negado")
    service = RideRequest(db)
    canceled_request = service.cancel_request(request_id)
    return canceled_request