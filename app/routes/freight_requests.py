from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.freight import FreightService
from app.schemas.freight import FreightCreate, FreightResponse
from app.auth.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

@router.post("/freights", response_model=FreightResponse)
async def create_freight(
    freight_data: FreightCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um novo frete e inicia matching"""

    if current_user['role'] != 'client':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access permitted only for client'
        )

    try:
        freight_service = FreightService(db)
        freight = await freight_service.create_freight(
            client_id=freight_data.client_id,
            pickup_address=freight_data.pickup_address,
            delivery_address=freight_data.delivery_address,
            freight_type=freight_data.freight_type,
            estimated_weight=freight_data.estimated_weight,
            estimated_volume=freight_data.estimated_volume,
            metadata=freight_data.metadata
        )

        return freight
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar frete: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{freight}/status", response_model=FreightResponse)
def get_freight_status(
    freight_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém o status completo de um frete"""
    if current_user['role'] != 'client':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access permitted only for client'
        )

    freight_service = FreightService(db)
    freight_status = freight_service.get_freight_status(freight_id)

    if not freight_status:
        raise HTTPException(status_code=404, detail="Frete não encontrado")

    return freight_status


@router.post("/{freight_id}/cancel")
def cancel_freight(
    freight_id: int,
    reason: str = "Solicitado pelo cliente",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancela um frete"""
    if current_user['role'] != 'client':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access permitted only for client'
        )
    freight_service = FreightService(db)
    success = freight_service.cancel_freight(freight_id, reason)

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não foi possível cancelar o frete")

    return {"success": True, "message": "Frete cancelado com sucesso"}
