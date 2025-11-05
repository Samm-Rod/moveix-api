# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.db.database import get_db
# from app.schemas.matching import MatchingResponse
# from app.auth.dependencies import get_current_user
# import logging
#
# logger = logging.getLogger(__name__)
#
# router = APIRouter(prefix="/api/v1")
#
# @router.get("/{matching_id}", response_model=MatchingResponse)
# def get_matching_status(
#     matching_id: int,
#     current_user = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Obtém o status de um processo de matching"""
#     from app.models.matching import Matching
#     if current_user['role'] != 'driver':
#         raise HTTPException(status_code=400, detail="Apenas drivers")
#
#     matching = db.query(Matching).filter(Matching.id == matching_id).first()
#     if not matching:
#         raise HTTPException(status_code=404, detail="Processo de matching não encontrado")
#
#     return matching
#
