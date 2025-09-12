# app/routes/matching_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.services.matching import MatchingService
from app.schemas.matching_schemas import (
    StartMatchingRequest,
    SelectDriverRequest,
    MatchingResponse,
    MatchingProgressResponse,
    MatchingStatsResponse,
)

import logging

logger = logging.getLogger(__name__)
route = APIRouter(prefix="/api/v1/matching")

@route.post("/start", response_model=MatchingResponse)
def start_matching(
    request_data: StartMatchingRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Request: ⚠️ {request_data}")
    if current_user['role'] != 'driver':
        logger.warning(f" ❌ Apenas drivers podem acessar !")
        raise HTTPException(status_code=403, detail='Apenas motoristas podem cadastrar ver matching')

    service = MatchingService(db)
    matching = service.start_matching(
        request_id=request_data.request_id,
        request_data=request_data
    )
    return matching


@route.post("/{matching_id}/select_driver", response_model=MatchingResponse)
def select_driver(
    matching_id: int,
    driver_data: SelectDriverRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MatchingService(db)
    matching = service.select_driver(
        matching_id=matching_id,
        driver_id=driver_data.driver_id,
        vehicle_id=driver_data.vehicle_id,
        price=driver_data.price,
        score=driver_data.score
    )
    return matching


# 🔹 3. Atualizar progresso (exibir status em tempo real)
@route.get("/{matching_id}/progress", response_model=MatchingProgressResponse)
def get_progress(
    matching_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MatchingService(db)
    progress = service.get_progress(matching_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Matching não encontrado")
    return progress


# 🔹 4. Confirmar corrida (quando motorista confirma no app)
@route.post("/{matching_id}/confirm", response_model=MatchingResponse)
def confirm_matching(
    matching_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MatchingService(db)
    matching = service.confirm_matching(matching_id)
    return matching


# 🔹 5. Cancelar matching
@route.post("/{matching_id}/cancel", response_model=MatchingResponse)
def cancel_matching(
    matching_id: int,
    reason: str = "Cancelado pelo usuário",
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MatchingService(db)
    matching = service.fail_matching(matching_id, reason)
    return matching


# 🔹 6. Estatísticas de matching (admin/relatórios)
@route.get("/stats", response_model=MatchingStatsResponse)
def get_matching_stats(
    period_days: int = 30,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MatchingService(db)
    stats = service.get_stats(period_days)
    return stats