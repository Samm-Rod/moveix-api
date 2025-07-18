# app/routes/payment.py
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.schemas.payments import PaymentCreate, PaymentOut
from app.services.payments import create_payment, confirm_payment
from app.auth.dependencies import get_db, get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post('/create', response_model=PaymentOut)
def create(
    payment: PaymentCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    return create_payment(payment, db, current_user)

@router.post('/confirm/{payment_id}')
def confirm(
    payment_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(security)
):
    return confirm_payment(payment_id, db, current_user)
