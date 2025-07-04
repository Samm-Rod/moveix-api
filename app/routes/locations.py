from fastapi import APIRouter, Query, HTTPException, status
from fastapi.params import Depends
from app.services.locations import geocode_reverso, geocodification
from app.auth.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post('/geocodification')
async def geocode(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await geocodification(db, current_user)


@router.post('/reverse')
async def reverse(
    lat: float = Query(...), 
    long: float = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
        return await geocode_reverso(lat, long, db, current_user)

    