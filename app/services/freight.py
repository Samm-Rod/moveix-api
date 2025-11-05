from typing import Optional, Dict, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import asyncio

from app.models.freight import Freight
from app.models.matching import Matching
from app.enums.freight_status import FreightStatus
from app.enums.matching_status import MatchingStatus
from app.services.matching import MatchingService
from shared.radar_api import RadarService

logger = logging.getLogger(__name__)

class FreightService:
    def __init__(self, db: Session):
        self.db = db
        self.radar_service = RadarService()

    async def create_freight(
            self,
            client_id: int,
            pickup_address: str,
            delivery_address: str,
            freight_type: str,
            estimated_weight: Optional[float] = None,
            estimated_volume: Optional[float] = None,
            metadata: Optional[Dict] = None
    ) -> Freight:
        """Cria um novo frete e inicia o processo de matching"""

        # Geocodificar endereços
        pickup_coords = await self.radar_service.geocode_address(pickup_address)
        delivery_coords = await self.radar_service.geocode_address(delivery_address)

        if not pickup_coords or not delivery_coords:
            logger.warning("❌ Não foi possível geocodificar os endereços")
            raise ValueError("Não foi possível geocodificar os endereços")

        # Calcular preço estimado
        estimated_price = await self._calculate_estimated_price(
            pickup_coords, delivery_coords, freight_type, estimated_weight
        )

        # Criar frete
        freight = Freight(
            client_id=client_id,
            pickup_address=pickup_address,
            pickup_lat=pickup_coords[0],
            pickup_lng=pickup_coords[1],
            delivery_address=delivery_address,
            delivery_lat=delivery_coords[0],
            delivery_lng=delivery_coords[1],
            freight_type=freight_type,
            estimated_weight=estimated_weight,
            estimated_volume=estimated_volume,
            estimated_price=estimated_price,
            request_metadata=metadata or {},
            status=FreightStatus.PENDING
        )

        self.db.add(freight)
        self.db.commit()
        self.db.refresh(freight)

        # Iniciar processo de matching
        asyncio.create_task(self._start_matching_process(freight.id))

        return freight

    async def _start_matching_process(self, freight_id: int):
        """Inicia o processo de matching em background"""
        try:
            matching_service = MatchingService(self.db)
            await matching_service.matching_in_process(freight_id)
            logger.warning(f"Iniciando o processo de matching ...")
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar matching para frete {freight_id}: {e}")
            # Marca frete como falha
            freight = self.db.query(Freight).filter(Freight.id == freight_id).first()
            if freight:
                freight.status = FreightStatus.CANCELLED
                freight.cancelled_at = datetime.now()
                self.db.commit()
            return freight

    async def _calculate_estimated_price(
            self,
            pickup_coords: Tuple[float, float],
            delivery_coords: Tuple[float, float],
            freight_type: str,
            weight: Optional[float]
    ) -> float:
        """Calcula preço estimado baseado na distância e tipo de frete"""
        route_info = await self.radar_service.get_route_distance(
            pickup_coords[0], pickup_coords[1],
            delivery_coords[0], delivery_coords[1]
        )

        if not route_info:
            # Fallback: cálculo simplificado
            base_price = 20.0
            distance_estimate = self._estimate_distance(pickup_coords, delivery_coords)
            return base_price + (distance_estimate * 2.5)

        # Preço baseado na distância e tipo de frete
        base_rate = 15.0
        km_rate = 2.0
        weight_rate = 0.5 if weight else 0

        price = base_rate + (route_info["distance_km"] * km_rate)
        if weight:
            price += weight * weight_rate

        # Ajustar por tipo de frete
        type_multipliers = {
            "urgent": 1.5,
            "fragile": 1.3,
            "large": 1.2,
            "standard": 1.0
        }

        multipliers = type_multipliers.get(freight_type.lower(), 1.0)
        return round(price * multipliers, 2)

    def _estimate_distance(
        self,
        coord1: Tuple[float, float],
        coord2: Tuple[float, float]
    )-> float:
        """Estimativa simplificada de distância (Haversine)"""
        from math import radians, sin, cos, sqrt, atan2

        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return 6371 * c # Distância em km

    def get_freight_status(self, freight_id: int) -> Optional[Dict]:
        """Obtém status completo do frete """
        freight = self.db.query(Freight).filter(Freight.id == freight_id).first()
        if not freight:
            return None

        matching = self.db.query(Matching).filter(
            Matching.freight_id == freight_id
        ).order_by(Matching.started_at.desc()).first()

        return {
            "freight": freight,
            "matching": matching,
            "driver": freight.driver if freight.driver else None,
            "current_status": freight.status.value
        }

    def starting_freight(self, freight_id: int) -> bool:
        """Inicia frete"""
        freight = self.db.query(Freight).filter(Freight.id == freight_id).first()
        match = self.db.query(Matching).filter(Matching.freight_id == freight_id).first()

        if not freight or freight.status != FreightStatus.ACCEPTED:
            return False

        if not match or match.status != MatchingStatus.MATCHED:
            return False

        freight.status = FreightStatus.STARTING
        freight.started_at = datetime.now()

        self.db.commit()
        return True


    def finished_freight(self, freight_id: int)-> bool:
        """Finalizar frete"""
        freight = self.db.query(Freight).filter(Freight.id == freight_id).first()
        if not freight or freight.status != FreightStatus.PENDING:
            return False

        freight.status = FreightStatus.COMPLETED
        freight.completed_at = datetime.now()

        self.db.commit()
        return True


    def cancel_freight(self, freight_id: int, reason: str)-> bool:
        """Cancela um frete"""
        freight = self.db.query(Freight).filter(Freight.id == freight_id).first()
        if not freight or freight.status != FreightStatus.PENDING:
            return False

        freight.status = FreightStatus.CANCELLED
        freight.cancelled_at = datetime.now()

        self.db.commit()
        return True










