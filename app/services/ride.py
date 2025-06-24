from app.models.ride import Ride
from app.schemas.ride import RideCreate
from app.models.driver import Driver
from app.models.client import Client
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

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

def new_ride(ride_data: dict, db: Session):
    # Busca cliente
    client = db.query(Client).filter(Client.id == ride_data["client_id"]).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Client not found"
        )
    # Não busca driver nem vehicle agora, pois serão preenchidos quando o motorista aceitar
    ride = Ride(
        client_id=ride_data["client_id"],
        driver_id=None,
        vehicle_id=None,
        start_location=ride_data["start_location"],
        end_location=ride_data["end_location"],
        distance=ride_data["distance"],
        duration=ride_data["duration"],
        fare=ride_data["fare"],
        status=ride_data["status"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    return ride


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