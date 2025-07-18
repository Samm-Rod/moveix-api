from fastapi import APIRouter, Query
from fastapi.params import Depends
from fastapi.security import HTTPBearer
from app.services.locations import geocode_reverso, geocodification, get_tracking, update_tracking
from app.auth.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session
from app.schemas.locations import LocationCreate


router = APIRouter()
security = HTTPBearer()

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
    current_user=Depends(security)
):
        return await geocode_reverso(lat, long, db, current_user)

@router.get('rides/{ride_id}/tracking')
def get_tracking_points(
      ride_id: int, 
      db: Session = Depends(get_db), 
      current_user=Depends(security)
):
      return get_tracking(ride_id, db, current_user)




@router.post("/track/update")
def track_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    return update_tracking(location, db, current_user)
