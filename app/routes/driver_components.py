from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.freight import FreightResponse
from app.models.driver_meta import DriverMeta
from app.services.freight import FreightService
from app.services.matching import MatchingService
from app.schemas.driver_offer import DriverOfferResponseRequest
from app.schemas.matching import MatchingResponse
from app.auth.dependencies import get_current_user
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

@router.get("/{matching_id}/status", response_model=MatchingResponse)
def get_status_matching(
    matching_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém o status de um processo de matching"""
    from app.models.matching import Matching
    if current_user['role'] != 'driver':
        logger.warning("Acesso apenas para Drivers ⚠️")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access for drivers only")

    matching = db.query(Matching).filter(Matching.id == matching_id).first()
    if not matching:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching not found ⚠️")

    return matching


@router.post("/{offer_id}/respond")
async def driver_respond(
        offer_id: int,
        response_data: DriverOfferResponseRequest,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Motorista responde a uma oferta"""
    """[True/False]"""
    if current_user['role'] != 'driver':
        logger.warning("Acesso apenas para Drivers ⚠️")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access permitted only for drivers'
        )

    matching_service = MatchingService(db)
    success = await matching_service.process_driver_response(offer_id, response_data.accepted)

    if not success:
        logger.warning("Oferta não encontrada ou já respondida ⚠️")
        raise HTTPException(status_code=404, detail="Offer not found or already answered")

    logger.info(f"Resultado do Matching: {response_data.accepted}")
    return {"success": True, "accepted": response_data.accepted}


@router.patch("freights/{freight_id}/start")
def start_freight(
        freight_id: int,
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Inicia a viagem"""
    if current_user['role'] != 'driver':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access permitted only for driver'
        )
    freight_service = FreightService(db)
    success = freight_service.starting_freight(freight_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível iniciar a viagem"
        )

    return {"success": True, "message": "Viagem iniciada ..."}

@router.patch("freights/{freight_id}/cancel")
def cancel_freight(
    freight_id: int,
    reason: str = "Solicitado pelo driver",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancela um frete"""
    if current_user['role'] != 'driver':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access permitted only for driver'
        )
    freight_service = FreightService(db)
    success = freight_service.cancel_freight(freight_id, reason)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível cancelar o frete"
        )

    return {"success": True, "message": "Frete cancelado com sucesso"}


"""Motorista finaliza o frete"""
@router.patch("/freights/{freight_id}/finish", response_model=FreightResponse)
async def finish_freight(
        freight_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem finalizar fretes"
        )

    from app.services.freight import FreightService
    freight_service = FreightService(db)
    return await freight_service.finished_freight(freight_id)


@router.post("/driver/ping")
def driver_ping(
    lat: float,
    lng: float,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user["role"] != "driver":
        raise HTTPException(status_code=403, detail="Somente motoristas podem usar este endpoint")

    driver_meta = db.query(DriverMeta).filter(DriverMeta.driver_id == current_user["user_id"]).first()
    if not driver_meta:
        raise HTTPException(status_code=404, detail="DriverMeta não encontrado")

    driver_meta.latitude = lat
    driver_meta.longitude = lng
    driver_meta.last_updated = datetime.now()
    driver_meta.is_online = True
    db.commit()
    return {"message": "Status atualizado"}

