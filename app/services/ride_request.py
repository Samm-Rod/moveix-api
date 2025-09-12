from fastapi import HTTPException, status
from app.models.request import Request
from app.models.matching import Matching
from app.schemas.trip_request import RequestRide, UpdateRide
from app.enums.request_status import TripRequestStatus
from app.models.client import Client
from datetime import datetime
from sqlalchemy.orm import Session
import asyncio

"""
    Solicitar uma corrida/viagem
    Buscar corrida por id
    Atualizar status
    
"""

class RideRequest:
    def __init__(self, db: Session):
        self.db = db

    # Criar corrida
    def create_request(self,client_id: int, request_data: RequestRide):
        new_request = Request(
            client_id=client_id,
            **request_data.model_dump()
        )
        new_request.status = TripRequestStatus.SEARCHING.value
        new_request.estimated_fare = 150.85   # Provisório
        self.db.add(new_request)
        self.db.commit()
        self.db.refresh(new_request)
        return new_request

    def view_my_request(self, request_id: int):
        request = self.db.query(Request).filter(Request.id == request_id).first()

        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )

        if request.status in [TripRequestStatus.COMPLETED.value, TripRequestStatus.CANCELED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request already {request.status.lower()}"
            )

        return request


    def update_request(self, request_id: int, request_data: UpdateRide):
        request = self.db.query(Request).filter(Request.id == request_id).first()

        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )

        for field, value in request_data.model_dump(exclude_unset=True).items():
            if value is None:
                continue
            if isinstance(value, str) and (value.strip() == "" or value.lower() == "string"):
                continue
            setattr(request, field, value)


        self.db.commit()
        self.db.refresh(request)
        return request


    def cancel_request(self, request_id: int):
        request = self.db.query(Request).filter(Request.id == request_id).first()

        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )

        # Se já estiver finalizado, não pode cancelar
        if request.status in [TripRequestStatus.COMPLETED.value, TripRequestStatus.CANCELED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Request already {request.status.lower()}"
            )

        request.status = TripRequestStatus.CANCELED.value
        self.db.commit()
        self.db.refresh(request)

        return request



