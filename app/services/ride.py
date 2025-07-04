# app/services/ride.py

from app.models.ride import Ride
from app.schemas.ride import RideCreate
from app.models.driver import Driver
from app.models.client import Client
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.utils.config import settings
import httpx

GOOGLE_API_KEY = settings.GOOGLE_MAPS_API_KEY

"""
 -> Nova corrida;
    - Início previsto (start_time)
    - Local de partida e destino
    - Status da corrida (ex: AGUARDANDO, EM_ANDAMENTO, FINALIZADA, CANCELADA)
    - Valor estiado da corrida

 -> Cancelar corrida;
    - Permite mudar o status da corrida 'CANCELADA'
    - Avaliação(Opcional)

 -> Iniciar corrida
     - Define start_time = datetime.now() e muda o status para 'EM_ANDAMENTO'
 
 -> Finalizar corrida
     - Define 'end_time' e muda o status da para 'FINALIZADA'
     - Avaliação

 -> Calcula valor da corrida
     + Baseado em:
     - Distância (pode usar lib de mapas ou mockar por enquanto)
     - Tempo estimado
     - Tarifa base do app

"""

def confirm_ride(ride_data: dict, db: Session, current: dict):
    """
    Confirma uma corrida baseada nos dados de simulação:
      - ride_data deve conter:
          client_id, driver_id,
          origin (start_location),
          destination (end_location),
          distance (km),
          duration (min),
          fare (R$)
    """
    # 1) Verifica permissão: só o cliente dono pode confirmar
    client = current["user"]
    if current["role"] != "client" or client.id != ride_data["client_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Apenas o cliente dono pode confirmar esta corrida")

    # 2) Verifica se o cliente existe
    db_client = db.query(Client).filter_by(id=ride_data["client_id"]).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    # 3) Verifica se o driver existe e está disponível
    driver = db.query(Driver).filter_by(id=ride_data["driver_id"], is_active=True).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado ou indisponível"
        )

    # 4) Cria a Ride
    ride = Ride(
        client_id=ride_data["client_id"],
        driver_id=driver.id,
        vehicle_id=driver.vehicles[0].id if driver.vehicles else None,
        start_location=ride_data["start_location"],
        end_location=ride_data["end_location"],
        distance=ride_data["distance"],
        duration=ride_data["duration"],
        fare=ride_data["fare"],
        status="em_andamento",       # já inicia como em andamento
        start_time=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(ride)

    # 5) Marca o motorista como ocupado
    driver.is_active = False

    # 6) Persiste tudo de uma vez
    db.commit()
    db.refresh(ride)
    return ride
    

# Calcula valor da corrida
def calculator_fare(driver: Driver, distance_km: float, duracao_min: float) -> float:
    base_fare = 5.00
    price_by_km = 2.50
    price_by_min = 0.50

    if driver.vehicles and driver.vehicles[0].model == 'truck': # isso se for caminhão
        price_by_km += 1.00
        price_by_min += 0.30

    # Pode haver outros tipos de transporte aqui
    # ...

    estimated_value = base_fare + (price_by_km * distance_km) + (price_by_min * duracao_min)
    return estimated_value

# Função de service para cálculo de rota entre dois pontos
async def calculator_ride(origin: str, destin: str, db: Session, current: dict):

    if current['role'] != 'client':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Apenas clientes podem simular corridas'
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://maps.googleapis.com/maps/api/directions/json',
                params={
                    'origin': origin,
                    'destination': destin,
                    'key': GOOGLE_API_KEY
                },
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            if data['status'] != 'OK':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Rota não encontrada'
                )

            leg = data['routes'][0]['legs'][0]
            distance_km = leg['distance']['value'] / 1000
            duration_min = leg['duration']['value'] / 60

            drivers = db.query(Driver).filter(Driver.is_active == True).all()

            options = []
            for driver in drivers:
                fare = calculator_fare(driver, distance_km, duration_min)
                options.append({
                    "driver_id": driver.id,
                    "driver_name": driver.name,
                    "vehicle": driver.vehicles[0].plate if driver.vehicles else None,
                    "distance_km": round(distance_km, 2),
                    "duration_min": round(duration_min, 1),
                    "estimated_fare": round(fare, 2),
                })

            return {
                'origin': leg['start_address'],
                'destination': leg['end_address'],
                'distance_km': round(distance_km, 2),
                'duration_min': round(duration_min, 1),
                'options': options
            }

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'Erro ao conectar com API do Google: {e}'
        )

def get_rides_by_client(client_id: int, db: Session):
    rides = db.query(Ride).filter(Ride.client_id == client_id).all()
    return rides


def cancel_ride(user_id: int, user_type: str, ride_id: int, db: Session):
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Corrida não encontrada"
        )

    if user_type == "client" and ride.client_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cliente não autorizado"
        )
    if user_type == "driver" and ride.driver_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Motorista não autorizado"
        )

    ride.status = "cancelled"
    ride.updated_at = datetime.now()
    db.commit()
    db.refresh(ride)
    return ride


def start_ride(driver_id: int, ride_id: int, db: Session):
    ride = db.query(Ride).filter_by(id=ride_id, driver_id=driver_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ride not found"
        )

    ride.status = "em_andamento"
    ride.start_time = datetime.now()
    ride.updated_at = datetime.now()
    db.commit()
    db.refresh(ride)
    return ride


def finish_ride(driver_id: int, ride_id: int, db: Session):
    ride = db.query(Ride).filter_by(id=ride_id, driver_id=driver_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ride not found"
        )

    ride.status = "finalizada"
    ride.end_time = datetime.now()
    ride.updated_at = datetime.now()
    db.commit()
    db.refresh(ride)
    return ride


def get_current_ride_by_client(client_id: int, db: Session):
    ride = db.query(Ride).filter(
        Ride.client_id == client_id,
        Ride.status.notin_(["finalizada", "cancelled"])
    ).order_by(Ride.created_at.desc()).first()
    return ride


def rate_ride(client_id: int, ride_id: int, rating: int, db: Session):
    ride = db.query(Ride).filter_by(id=ride_id, client_id=client_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrida não encontrada para este cliente"
        )
    if ride.status != "finalizada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível avaliar corridas finalizadas"
        )
    if ride.rating is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta corrida já foi avaliada"
        )
    if not (0 <= rating <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A avaliação deve ser entre 0 e 5"
        )
    ride.rating = rating
    ride.updated_at = datetime.now()
    db.commit()
    db.refresh(ride)
    return ride

# Listar corridas disponíveis para motoristas

def get_available_rides(db: Session):
    return db.query(Ride).filter(Ride.status == "disponivel").all()

# Motorista aceita corrida (pega a corrida)
def accept_ride_service(driver, ride_id: int, db: Session):
    ride = db.query(Ride).filter(Ride.id == ride_id, Ride.status == "disponivel").first()
    if not ride:
        raise HTTPException(status_code=404, detail="Corrida não disponível para aceitação")
    if not driver.vehicles:
        raise HTTPException(status_code=400, detail="Motorista não tem veículo cadastrado")
    ride.driver_id = driver.id
    ride.vehicle_id = driver.vehicles[0].id
    ride.status = "em_andamento"
    ride.start_time = datetime.now()
    ride.updated_at = datetime.now()
    db.commit()
    db.refresh(ride)
    return ride

# Listar corridas do driver (em andamento ou histórico)
def get_rides_by_driver(driver_id: int, db: Session):
    return db.query(Ride).filter(Ride.driver_id == driver_id).all()