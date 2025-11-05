import httpx
from typing import Dict, List, Optional, Tuple, Any
from app.models.driver import Driver
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import os
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class RadarService:
    def __init__(self):
        self.api_key = os.getenv("RADAR_API_KEY")
        self.base_url = "https://api.radar.io/v1"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_route_distance(
            self,
            origin_lat: float,
            origin_lng: float,
            dest_lat: float,
            dest_lng: float
    ) -> Optional[Dict]:
        """Obtém distância e tempo de rota entre dois pontos"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                origin = f"{origin_lat},{origin_lng}"
                destination = f"{dest_lat},{dest_lng}"

                response = await client.get(
                    f"{self.base_url}/route/distance",
                    params={
                        "origin": origin,
                        "destination": destination,
                        "modes": "car",
                        "units": "metric"
                    },
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("routes") and data["routes"][0]["legs"]:
                        leg = data["routes"][0]["legs"][0]
                        return {
                            "distance_km": leg["distance"]["value"] / 1000,
                            "duration_seconds": leg["duration"]["value"],
                            "polyline": data["routes"][0]["geometry"]
                        }
                else:
                    logger.error(f"Erro na API Radar: {response.status_code} - {response.text}")

                return None

        except Exception as e:
            logger.error(f"Erro ao obter rota do Radar: {e}")
            return None

    async def get_distance_matrix(
            self,
            origin: List[Tuple[float, float]],
            destination: List[Tuple[float, float]]
    ) -> Optional[List[Dict]]:
        """Obtém matriz de distância entre múltiplos pontos"""
        try:
            origin_str = "|".join([f"{lat},{lng}" for lat, lng in origin])
            destination_str = "|".join([f"{lat},{lng}" for lat, lng in destination])

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/route/distance",
                    params={
                        "origin": origin_str,
                        "destination": destination_str,
                        "modes": "car",
                        "units": "metric"
                    },
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for row in data.get("rows", []):
                        for element in row.get("elements", []):
                            if element.get("status") == "OK":
                                results.append({
                                    "distance_km": element["distance"]["value"] / 1000,
                                    "duration_seconds": element["duration"]["value"]
                                })
                            else:
                                results.append(None)
                    return results
                else:
                    logger.error(f"Erro na matriz de distância: {response.status_code} - {response.text}")

                return None

        except Exception as e:
            logger.error(f"Erro na matriz de distância: {e}")
            return None

    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Converte endereço em coordenadas"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/geocode/forward",
                    params={"query": address},
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("addresses"):
                        coords = data["addresses"][0]
                        return (coords["latitude"], coords["longitude"])
                else:
                    logger.error(f"Erro no geocoding: {response.status_code} - {response.text}")

                return None

        except Exception as e:
            logger.error(f"Erro no geocoding: {e}")
            return None

    async def get_drivers_within_radius(
            self,
            db: Session,
            pickup_lat: float,
            pickup_lng: float,
            radius_km: float,
            min_rating: float = 3.0,
            vehicle_types: Optional[List[str]] = None
    ) -> List[Driver]:
        """
        Encontra motoristas dentro do raio especificado usando busca aproximada
        e depois filtra com API do Radar para precisão
        """
        try:
            # Primeiro: busca aproximada no banco (rápida)
            approximate_drivers = self._get_approximate_drivers(
                db, pickup_lat, pickup_lng, radius_km, min_rating, vehicle_types
            )

            if not approximate_drivers:
                logger.info(f"Nenhum motorista encontrado no raio de {radius_km}km")
                return []

            logger.info(f"Encontrados {len(approximate_drivers)} motoristas próximos (busca aproximada)")

            # Segundo: filtrar com API do Radar para distância real
            origin = [(pickup_lat, pickup_lng)]
            destination = [
                (driver.meta.latitude, driver.meta.longitude)
                for driver in approximate_drivers
                if driver.meta and driver.meta.latitude and driver.meta.longitude
            ]

            if not destination:
                logger.warning("Nenhum motorista com coordenadas válidas")
                return []

            distances = await self.get_distance_matrix(origin, destination)

            if not distances:
                logger.warning("Não foi possível calcular distâncias via API")
                # Fallback: retornar motoristas sem distância calculada
                return approximate_drivers

            valid_drivers = []
            for i, driver in enumerate(approximate_drivers):
                if i < len(distances) and distances[i]:
                    if distances[i]["distance_km"] <= radius_km:
                        driver.distance_km = distances[i]["distance_km"]
                        driver.duration_seconds = distances[i]["duration_seconds"]
                        valid_drivers.append(driver)

            logger.info(f"{len(valid_drivers)} motoristas dentro do raio real de {radius_km}km")
            return sorted(valid_drivers, key=lambda x: x.distance_km)

        except Exception as e:
            logger.error(f"Erro ao buscar motoristas: {e}", exc_info=True)
            return []

    def _get_approximate_drivers(
            self,
            db: Session,
            lat: float,
            lng: float,
            radius_km: float,
            min_rating: float,
            vehicle_types: Optional[List[str]] = None
    ) -> list[type[Driver]]:
        """Busca aproximada de motoristas online próximos"""
        from app.models.search_helper import SearchHelper
        from app.models.driver_meta import DriverMeta
        from sqlalchemy import func
        import math

        # Calcular limites aproximados (bounding box)
        earth_radius_km = 6371
        lat_diff = (radius_km / earth_radius_km) * (180 / math.pi)

        # Ajustar longitude pela latitude (a circunferência diminui perto dos polos)
        lng_diff = lat_diff / max(math.cos(math.radians(lat)), 0.01)

        logger.info(f"Buscando motoristas em: lat={lat}±{lat_diff}, lng={lng}±{lng_diff}")

        # ✅ Query corrigida
        query = db.query(Driver).join(DriverMeta).filter(
            DriverMeta.is_online == True,
            DriverMeta.is_available == True,
            DriverMeta.last_updated >= datetime.now(timezone.utc) - timedelta(minutes=5),
            or_(
                DriverMeta.rating >= min_rating,
                DriverMeta.rating == None
            ),
            # ✅ CORREÇÃO: latitude filtrada por latitude, longitude por longitude
            DriverMeta.latitude.between(lat - lat_diff, lat + lat_diff),
            DriverMeta.longitude.between(lng - lng_diff, lng + lng_diff)
        )

        if vehicle_types and hasattr(Driver, "vehicle_type"):
            query = query.filter(Driver.vehicle_type.in_(vehicle_types))

        drivers = query.all()
        logger.info(f"Query retornou {len(drivers)} motoristas online")

        return drivers