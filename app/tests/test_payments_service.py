from sqlalchemy.orm.session import Session
from app.models.ride import Ride
from app.models.client import Client
from app.schemas.payments import PaymentCreate
from app.services.payments import create_payment
from datetime import datetime

def test_create_payment_success(db: Session):
    # Cria um cliente fake
    
    client = Client(
        name="Teste",
        email="teste@email.com",
        hashed_password="fakehashed123",  # ✅ valor mockado
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    # Cria uma corrida fake
    ride = Ride(client_id=client.id, driver_id=2, start_location="A", end_location="B",
                distance=10.0, duration=15, fare=50.0, status="em_andamento")
    db.add(ride)
    db.commit()
    db.refresh(ride)

    # Prepara os dados para o pagamento
    payment_data = PaymentCreate(
        ride_id=ride.id,  # type: ignore
        amount=ride.fare,  # type: ignore
        payment_method="pix"
    )

    # Usuário autenticado simulado
    current_user = {
        "user": client,
        "role": "client"
    }

    result = create_payment(payment_data=payment_data, db=db, current_user=current_user)

    assert result.ride_id == ride.id  # type: ignore
    assert result.amount == ride.fare  # type: ignore
    assert result.status == "pending"  # type: ignore
    assert "mockpagamento.com/pay" in result.fake_payment_url  # type: ignore
