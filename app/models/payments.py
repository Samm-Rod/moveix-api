
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class Payment(Base):

    __tablename__='payments'

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey('rides.id'))
    amount = Column(Float, nullable=False)
    status = Column(String, default='pending')
    payment_method = Column(String, default='pix')
    fake_payment_url = Column(String) # simulação de URL para pagar

    ride = relationship('Ride', back_populates='payment')

    