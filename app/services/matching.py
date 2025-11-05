import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import logging

from app.models.matching import Matching
from app.models.freight import Freight
from app.models.driver import Driver
from app.models.driver_offer import DriverOffer
from app.enums.matching_status import MatchingStatus
from app.enums.request_status import TripRequestStatus
from shared.radar_api import RadarService

logger = logging.getLogger(__name__)


class MatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.radar_service = RadarService()
        self.offer_timeout = 15  # segundos

    async def matching_in_process(self, freight_id: int) -> Matching:
        """Inicia o processo de matching para um frete"""
        freight = self.db.query(Freight).filter(Freight.id == freight_id).first()
        if not freight:
            raise ValueError("Freight não encontrado")

        # ✅ Criar registro de matching com UTC
        matching = Matching(
            freight_id=freight_id,
            status=MatchingStatus.SEARCHING,
            started_at=datetime.now(timezone.utc),  # ✅ UTC aware
            search_radius_km=2.0,
            max_search_radius_km=50.0,
            min_driver_rating=4.0
        )

        self.db.add(matching)
        self.db.commit()
        self.db.refresh(matching)

        # Passar apenas o ID para evitar detachment
        matching_id = matching.id

        # Iniciar processo assíncrono
        asyncio.create_task(self._matching_worker(matching_id))

        return matching

    async def _matching_worker(self, matching_id: int):
        """Worker assíncrono para processar o matching"""
        try:
            # SEMPRE recarregar da sessão no início
            matching = self.db.query(Matching).filter(
                Matching.id == matching_id
            ).first()

            if not matching:
                logger.error(f"Matching {matching_id} não encontrado")
                return

            freight = self.db.query(Freight).filter(
                Freight.id == matching.freight_id
            ).first()

            if not freight:
                matching.set_failed("Freight não encontrado")
                self.db.commit()
                return

            # Buscar motoristas próximos
            drivers = await self.radar_service.get_drivers_within_radius(
                self.db,
                freight.pickup_lat,
                freight.pickup_lng,
                matching.search_radius_km,
                matching.min_driver_rating,
                self._parse_vehicle_types(matching.preferred_vehicle_types)
            )

            matching.drivers_found_count = len(drivers)
            self.db.commit()

            if not drivers:
                # Expandir raio de busca se necessário
                if matching.search_radius_km < matching.max_search_radius_km:
                    new_radius = matching.search_radius_km * 1.5
                    matching.search_radius_km = new_radius
                    self.db.commit()

                    logger.info(f"Expandindo busca para {new_radius}km")
                    await asyncio.sleep(1)

                    # Passar apenas o ID, não o objeto
                    await self._matching_worker(matching_id)
                    return
                else:
                    matching.set_failed("Nenhum motorista encontrado")
                    self.db.commit()
                    return

            matching.status = MatchingStatus.DRIVERS_FOUND
            self.db.commit()

            # Enviar ofertas para motoristas
            await self._send_offers_to_drivers(matching, freight, drivers)

        except Exception as e:
            logger.error(f"Erro no matching worker: {e}", exc_info=True)

            # Recarregar matching antes de usar
            try:
                matching = self.db.query(Matching).filter(
                    Matching.id == matching_id
                ).first()
                if matching:
                    matching.set_failed(f"Erro interno: {str(e)}")
                    self.db.commit()
            except Exception as commit_error:
                logger.error(f"Erro ao salvar falha: {commit_error}")
                self.db.rollback()

    async def _send_offers_to_drivers(
            self,
            matching: Matching,
            freight: Freight,
            drivers: List[Driver]
    ):
        """Envia ofertas para motoristas e aguarda respostas"""
        # Salvar IDs antes de qualquer commit
        matching_id = matching.id

        matching.status = MatchingStatus.OFFERS_SENT
        matching.first_offer_sent_at = datetime.now(timezone.utc)  # ✅ UTC aware
        self.db.commit()

        estimated_pickup = datetime.now(timezone.utc) + timedelta(minutes=15)
        offer_ids = []
        for driver in drivers[:10]:
            offer = DriverOffer(
                driver_id=driver.id,
                helper_id=1,
                offered_price=freight.estimated_price,
                estimated_pickup_time=estimated_pickup,
                compatibility_score=0.85,
                response=TripRequestStatus.PENDING,
                offer_expires_at=datetime.now(timezone.utc) + timedelta(seconds=self.offer_timeout)  # ✅ UTC aware
            )
            self.db.add(offer)
            self.db.commit()
            self.db.refresh(offer)

            offer_ids.append(offer.id)

            # Enviar notificação push
            await self._send_push_notification(driver, freight)

        # Recarregar matching após commits
        matching = self.db.query(Matching).filter(
            Matching.id == matching_id
        ).first()

        matching.offers_sent_count = len(offer_ids)
        self.db.commit()

        # Criar tasks com IDs
        response_tasks = [
            self._wait_for_driver_response(offer_id)
            for offer_id in offer_ids
        ]

        # Aguardar respostas com timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*response_tasks, return_exceptions=True),
                timeout=self.offer_timeout + 5
            )
        except asyncio.TimeoutError:
            logger.info(f"Timeout no matching {matching_id}")

        # Recarregar antes de verificar resultado
        matching = self.db.query(Matching).filter(
            Matching.id == matching_id
        ).first()

        # Verificar se algum motorista aceitou
        accepted_offer = self.db.query(DriverOffer).filter(
            DriverOffer.id.in_(offer_ids),
            DriverOffer.response == TripRequestStatus.ACCEPTED
        ).first()

        if accepted_offer:
            matching.set_matched(
                accepted_offer.driver_id,
                accepted_offer.driver.vehicles[0].id if accepted_offer.driver.vehicles else None,
                accepted_offer.offered_price,
                1.0
            )
        else:
            matching.set_failed("Nenhum motorista aceitou a oferta")

        self.db.commit()
        return accepted_offer

    async def _wait_for_driver_response(self, offer_id: int):
        """Aguarda resposta do motorista com timeout"""
        try:
            await asyncio.sleep(self.offer_timeout)

            # Recarregar da sessão
            offer = self.db.query(DriverOffer).filter(
                DriverOffer.id == offer_id
            ).first()

            if offer and offer.response == TripRequestStatus.PENDING:
                offer.response = TripRequestStatus.TIMEOUT
                self.db.commit()

                matching = self.db.query(Matching).filter(
                    Matching.id == offer.matching_id
                ).first()

                if matching:
                    matching.timeout_count += 1
                    self.db.commit()

        except Exception as e:
            logger.error(f"Erro ao aguardar resposta: {e}")
            self.db.rollback()

    async def process_driver_response(
            self,
            offer_id: int,
            accepted: bool
    ) -> bool:
        """Processa resposta do motorista"""
        try:
            offer = self.db.query(DriverOffer).filter(
                DriverOffer.id == offer_id
            ).first()

            if not offer or offer.response != TripRequestStatus.PENDING:
                return False

            matching = self.db.query(Matching).filter(
                Matching.driver_offer_id == offer_id
            ).first()

            if not matching:
                return False

            if accepted:
                offer.response = TripRequestStatus.ACCEPTED
                offer.responded_at = datetime.now(timezone.utc)  # ✅ UTC aware
                logger.info(f"✅ Driver aceitou viagem {offer_id}")

                # Rejeitar outras ofertas do mesmo freight
                other_offers = self.db.query(DriverOffer).join(
                    Matching, Matching.driver_offer_id == DriverOffer.id
                ).filter(
                    Matching.freight_id == matching.freight_id,
                    DriverOffer.id != offer_id,
                    DriverOffer.response == TripRequestStatus.PENDING
                ).all()

                for other_offer in other_offers:
                    other_offer.response = TripRequestStatus.REJECTED
                    other_offer.responded_at = datetime.now(timezone.utc)  # ✅ UTC aware

                matching.driver_offer_id = offer_id
                matching.selected_driver_id = offer.driver_id

            else:
                offer.response = TripRequestStatus.REJECTED
                offer.responded_at = datetime.now(timezone.utc)  # ✅ UTC aware
                matching.declined_count += 1
                logger.warning(f"❌ Driver rejeitou viagem {offer_id}")

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Erro ao processar resposta: {e}")
            self.db.rollback()
            return False

    def _parse_vehicle_types(self, vehicle_types_str: Optional[str]) -> Optional[List[str]]:
        """Parseia string de tipos de veículo"""
        if not vehicle_types_str:
            return None
        return [vt.strip() for vt in vehicle_types_str.split(",")]

    async def _send_push_notification(self, driver: Driver, freight: Freight):
        """Envia notificação push para o motorista"""
        logger.info(f"Notificação enviada para motorista {driver.id} - Frete {freight.id}")
        pass