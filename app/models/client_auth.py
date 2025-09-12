from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class ClientAuth(Base):
    __tablename__ = "client_auth"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, unique=True)

    hashed_password = Column(String, nullable=False)
    two_fa_secret = Column(String, nullable=True)
    reset_code = Column(String, nullable=True)

    # Relacionamento Client_auth : Client
    client = relationship("Client", back_populates="auth")
