from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.rating import FreightRating, FreightRatingOut
from app.models.rating import Rating
from app.models.freight import Freight
from datetime import datetime
from typing import List, Optional

class RatingService:
    def __init__(self, db: Session):
        self.db = db

    async def rate_freight(self, client_id: int, freight_id: int, rating_data: FreightRating) -> FreightRatingOut:
        """Avalia um frete concluído"""
        # Verifica se o frete existe e está concluído
        freight = self.db.query(Freight).filter(
            Freight.id == freight_id,
            Freight.client_id == client_id,
            Freight.status == "completed"
        ).first()

        if not freight:
            raise ValueError("Frete não encontrado ou não está concluído")

        # Cria a avaliação
        rating = Rating(
            freight_id=freight_id,
            client_id=client_id,
            rated_user_id=freight.driver_id,
            rating=rating_data.rating,
            comment=rating_data.comment,
            created_at=datetime.utcnow(),
            user_type="driver"  # por enquanto só avalia motorista
        )

        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)

        return FreightRatingOut(**rating.__dict__)

    async def get_freight_ratings(self, freight_id: int) -> List[FreightRatingOut]:
        """Obtém avaliações de um frete específico"""
        ratings = self.db.query(Rating).filter(Rating.freight_id == freight_id).all()
        return [FreightRatingOut(**r.__dict__) for r in ratings]

    async def get_user_ratings(self, user_id: int, user_type: str, 
                             limit: Optional[int] = None, public_only: bool = False) -> List[FreightRatingOut]:
        """Obtém avaliações de um usuário (motorista ou ajudante)"""
        query = self.db.query(Rating).filter(
            Rating.rated_user_id == user_id,
            Rating.user_type == user_type
        )

        if public_only:
            query = query.filter(Rating.comment.isnot(None))

        if limit:
            query = query.limit(limit)

        ratings = query.all()
        return [FreightRatingOut(**r.__dict__) for r in ratings]
