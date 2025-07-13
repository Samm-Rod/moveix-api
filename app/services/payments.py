# app/services/payment.py
import random
from app.models.payments import Payment
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.payments import PaymentCreate
from app.models.ride import Ride

def create_payment(payment_data: PaymentCreate, db: Session, current_user: dict):
    user = current_user["user"]
    role = current_user["role"]

    # Verifica se a corrida existe
    ride = db.query(Ride).filter(Ride.id == payment_data.ride_id).first()
    if not ride:
        print('Corrida não encontrada')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrida não encontrada"
        )

    # (Opcional) Verifica se é o cliente dono da corrida
    if role == "client" and ride.client_id != user.id:
        print('Apenas o cliente dono pode realizar o pagamento')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o cliente dono pode realizar o pagamento"
        )

    # Cria pagamento mockado
    payment = Payment(
        ride_id=ride.id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        status="pending",
        fake_payment_url=f"https://mockpagamento.com/pay/{random.randint(10000, 99999)}"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment



def confirm_payment(payment_id: int, db: Session, current_user: dict):
    user = current_user["user"]
    role = current_user["role"]

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        print('Pagamento não encontrado')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado"
        )

    # Verifica se o pagamento pertence a uma corrida do cliente logado
    if role == "client":
        ride = db.query(Ride).filter(Ride.id == payment.ride_id).first()
        if not ride or ride.client_id != user.id:
            print('Você não tem permissão para confirmar este pagamento')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para confirmar este pagamento"
            )

    # Atualiza status do pagamento
    payment.status = "paid"
    db.commit()
    db.refresh(payment)

    return {"msg": "Pagamento confirmado com sucesso"}

