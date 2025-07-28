# app/services/locations.py

from fastapi import HTTPException, status
import httpx
from app.utils.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.locations import Location
from datetime import datetime
from app.models.ride import Ride
from app.schemas.locations import LocationCreate


GOOGLE_app_KEY = settings.GOOGLE_MAPS_app_KEY
BASE_URL = "https://maps.googleapps.com/maps/app/geocode/json"


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
            params={'address': address,'key': GOOGLE_app_KEY}
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
                params={'latlng': f'{lat},{long}', 'key': GOOGLE_app_KEY}
            )
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(502, f'Google app offline: {e}')

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


# Fluxo básico de rastreamento com gravação periódica
# def tracking_location(lat:str, long: str, db: Session):

#     try
        
#     except Exception as e:

# Rastrear corrida / exibe a corrida em tempo real 
def get_tracking(ride_id: int, db: Session, current_user: dict):
    # Verifica se a corrida existe
    ride = db.query(Ride).filter(Ride.id == ride_id).first()

    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Corrida não encontrada!'
        )

    # Restringe acesso ao cliente dono da corrida
    if current_user["role"] == "client" and ride.client_id != current_user["user"].id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )

    # Consulta os pontos de localização (últimos 50, por exemplo)
    locations = db.query(Location)\
        .filter(Location.ride_id == ride_id)\
        .order_by(Location.timestamp.desc())\
        .limit(50)\
        .all()

    return [
        {
            "lat": float(loc.latitude),
            "lng": float(loc.longitude),
            "timestamp": loc.timestamp
        } for loc in reversed(locations)
    ]


def update_tracking(location: LocationCreate, db: Session, current_user: dict):
    user = current_user["user"]
    role = current_user["role"]

    if role != "driver":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Somente motoristas podem enviar localização")

    # Pega a corrida mais recente do motorista que ainda está em andamento
    ride = db.query(Ride).filter(
        Ride.driver_id == user.id,
        Ride.status == "em_andamento"
    ).order_by(Ride.id.desc()).first()

    if not ride:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nenhuma corrida ativa encontrada")

    # Cria e grava nova localização
    loc = Location(
        ride_id=ride.id,
        latitude=str(location.latitude),
        longitude=str(location.longitude),
        timestamp=datetime.now()
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)

    return {"msg": "Localização registrada", "timestamp": loc.timestamp}


