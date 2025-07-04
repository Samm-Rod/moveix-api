# app/services/locations.py

from fastapi import HTTPException, status
import httpx
from app.utils.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.locations import Location
from datetime import datetime
from app.models.ride import Ride
from app.models.driver import Driver



GOOGLE_API_KEY = settings.GOOGLE_MAPS_API_KEY
BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


# 🧭 Geocodificação (endereço → coordenadas) + salva no banco
# Ela pega um endereço (Brasília - DF) e transforma em coordenadas GPS(Latitude e Longetude)

async def geocodification(db: Session, current: dict):

    user = current['user']
    role = current['role']

    if role == 'driver':
        ride = db.query(Ride)\
            .filter(Ride.driver_id == user.id)\
            .order_by(Ride.id.desc())\
            .first()
    elif role == 'client':
        ride = db.query(Ride)\
        .filter(Ride.client_id == user.id)\
        .order_by(Ride.id.desc())\
        .first()
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Acessp negado para este tipo de usuário'
        )
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Nenhuma corrida encontrada'
        )
    
    address = ride.start_location


    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}",
            params={'address': address,'key': GOOGLE_API_KEY}
        )
        data = response.json()
        print(data)

        if data.get("status") == "OK":
            location_data = data["results"][0]["geometry"]["location"]
            location = Location(
                ride_id=ride.id,
                latitude=str(location_data["lat"]),
                longitude=str(location_data["lng"]),
                timestamp=datetime.now()
            )
            db.add(location)
            db.commit()
            db.refresh(location)
            return location
        else:
            return {"error": "Endereço inválido ou não encontrado"}

# 🔁 Geocodificação reversa (lat/lng → endereço) + salva no banco
# Ela pega as coordenadas (Latitude e longetude) e descobre o endereço real ex:(Lago Sul - DF)
async def geocode_reverso(lat: float, long: float, db: Session, current: dict):
    user, role = current['user'], current['role']

    if role == 'driver':
        ride = db.query(Ride).filter(Ride.driver_id == user.id).order_by(Ride.id.desc()).first()
    elif role == 'client':
        ride = db.query(Ride).filter(Ride.client_id == user.id).order_by(Ride.id.desc()).first()
    else:
        raise HTTPException(403, 'Acesso negado')

    if not ride:
        raise HTTPException(404, 'Nenhuma corrida encontrada')

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                BASE_URL,
                params={'latlng': f'{lat},{long}', 'key': GOOGLE_API_KEY}
            )
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(502, f'Google API offline: {e}')

    data = resp.json()
    if data.get('status') != 'OK':
        raise HTTPException(400, 'Coordenadas sem endereço válido')

    loc = Location(
        ride_id=ride.id,
        latitude=str(lat),
        longitude=str(long),
        timestamp=datetime.now()
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)

    return {
        'ride_id': ride.id,
        'lat': lat,
        'long': long,
        'formatted_address': data['results'][0]['formatted_address'],
        'timestamp': loc.timestamp
    }






