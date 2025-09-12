from datetime import datetime, timedelta
from fastapi import requests
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.demand_analytics import DemandAnalytics
from app.models.surge_zone import SurgeZone
from app.models.ride import Ride
from app.models.driver import Driver

from typing import Dict
import logging

logger = logging.getLogger(__name__)

class DynamicPricingService:
    def __init__(self, db: Session):
        self.db = db
        self.base_price_per_km = 4.50
        self.base_price_per_minute = 0.75

    def calculate_dynamic_price(
        self, 
        origin_lat: float, 
        origin_lng: float,
        distance_km: float,
        duration_minutes: float,
        freight_type: str = "standard"
    ) -> Dict:
        """Calcula preço dinâmico baseado em múltiplos fatores"""
        
        # 1. Preço base
        base_price = self._calculate_base_price(distance_km, duration_minutes, freight_type)
        
        # 2. Multiplicador de demanda vs oferta
        demand_multiplier = self._get_demand_multiplier(origin_lat, origin_lng)
        
        # 3. Multiplicador temporal (hora do dia, dia da semana)
        time_multiplier = self._get_time_multiplier()
        
        # 4. Multiplicador climático
        weather_multiplier = self._get_weather_multiplier(origin_lat, origin_lng)
        
        # 5. Multiplicador de eventos especiais
        event_multiplier = self._get_event_multiplier(origin_lat, origin_lng)
        
        # 6. Multiplicador de zona de surge
        surge_multiplier = self._get_surge_zone_multiplier(origin_lat, origin_lng)
        
        # Cálculo final
        total_multiplier = (
            demand_multiplier * 
            time_multiplier * 
            weather_multiplier * 
            event_multiplier * 
            surge_multiplier
        )
        
        # Limitar multiplicador (não pode passar de 3x nem ser menor que 0.8x)
        total_multiplier = max(0.8, min(3.0, total_multiplier))
        
        final_price = base_price * total_multiplier
        
        return {
            "base_price": round(base_price, 2),
            "final_price": round(final_price, 2),
            "multiplier": round(total_multiplier, 2),
            "breakdown": {
                "demand_factor": round(demand_multiplier, 2),
                "time_factor": round(time_multiplier, 2),
                "weather_factor": round(weather_multiplier, 2),
                "event_factor": round(event_multiplier, 2),
                "surge_factor": round(surge_multiplier, 2)
            },
            "explanation": self._generate_explanation(total_multiplier),
            "valid_until": datetime.now() + timedelta(minutes=10)
        }
    

    def _calculate_base_price(self, distance_km: float, duration_minutes: float, freight_type: str) -> float:
        """Preço base sem multiplicadores"""
        distance_cost = distance_km * self.base_price_per_km
        time_cost = duration_minutes * self.base_price_per_minute
        
        # Multiplicador por tipo de frete
        type_multipliers = {
            "standard": 1.0,
            "fragile": 1.3,
            "heavy": 1.4,
            "furniture": 1.5,
            "urgent": 1.8
        }
        
        base_price = (distance_cost + time_cost) * type_multipliers.get(freight_type, 1.0)
        
        # Preço mínimo
        return max(base_price, 80.0)
    
    
    def _get_demand_multiplier(self, lat: float, lng: float) -> float:
        """Multiplicador baseado em demanda vs oferta atual"""
        try:
            # Área de 10km ao redor do ponto
            area_radius = 0.1  # ~10km in degrees
            
            # Contar solicitações nas últimas 2 horas
            two_hours_ago = datetime.now() - timedelta(hours=2)
            recent_requests = self.db.query(Ride).filter(
                Ride.pickup_latitude.between(lat - area_radius, lat + area_radius),
                Ride.pickup_longitude.between(lng - area_radius, lng + area_radius),
                Ride.created_at >= two_hours_ago
            ).count()
            
            # Contar motoristas disponíveis na área
            available_drivers = self.db.query(Driver).filter(
                Driver.is_available == True,
                Driver.current_latitude.between(lat - area_radius, lat + area_radius),
                Driver.current_longitude.between(lng - area_radius, lng + area_radius)
            ).count()
            
            if available_drivers == 0:
                return 2.0  # Alta demanda, zero oferta
            
            demand_ratio = recent_requests / max(available_drivers, 1)
            
            # Converter ratio em multiplicador
            if demand_ratio >= 3.0:
                return 2.0      # Demanda muito alta
            elif demand_ratio >= 2.0:
                return 1.5      # Demanda alta
            elif demand_ratio >= 1.0:
                return 1.2      # Demanda moderada
            elif demand_ratio >= 0.5:
                return 1.0      # Demanda normal
            else:
                return 0.9      # Demanda baixa = desconto!
                
        except Exception as e:
            logger.error(f"Erro ao calcular demand multiplier: {e}")
            return 1.0
        
    def _get_time_multiplier(self) -> float:
        """Multiplicador baseado no horário"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=segunda, 6=domingo
        
        # Horários de pico
        morning_peak = 7 <= hour <= 9      # 7h-9h
        evening_peak = 17 <= hour <= 19    # 17h-19h
        late_night = 22 <= hour or hour <= 5  # 22h-5h
        weekend = weekday >= 5             # Sábado/Domingo
        
        multiplier = 1.0
        
        if late_night:
            multiplier += 0.3  # +30% madrugada
        elif morning_peak or evening_peak:
            multiplier += 0.2  # +20% horário de pico
            
        if weekend:
            multiplier += 0.1  # +10% fim de semana
            
        return multiplier
    

    def _get_weather_multiplier(self, lat: float, lng: float) -> float:
        """Multiplicador baseado no clima"""
        try:
            # Integração com API de clima (OpenWeatherMap)
            weather_data = self._fetch_weather(lat, lng)
            
            if not weather_data:
                return 1.0
            
            weather_condition = weather_data.get('weather', [{}])[0].get('main', '').lower()
            
            weather_multipliers = {
                'rain': 1.3,        # +30% chuva
                'thunderstorm': 1.4, # +40% tempestade
                'snow': 1.5,        # +50% neve (raro no Brasil)
                'fog': 1.2,         # +20% neblina
                'clear': 1.0,       # Normal
                'clouds': 1.0       # Normal
            }
            
            return weather_multipliers.get(weather_condition, 1.0)
            
        except Exception as e:
            logger.error(f"Erro ao obter clima: {e}")
            return 1.0
        

    def _get_event_multiplier(self, lat: float, lng: float) -> float:
        """Multiplicador baseado em eventos especiais"""
        # Lista de eventos conhecidos (poderia vir de API ou admin)
        special_events = self._check_special_events(lat, lng)
        
        if special_events:
            return 1.4  # +40% durante eventos
        return 1.0  


    def _get_surge_zone_multiplier(self, lat: float, lng: float) -> float:
        """Multiplicador de zonas de surge predefinidas"""
        try:
            # Buscar zona mais próxima
            surge_zone = self.db.query(SurgeZone).filter(
                SurgeZone.is_active == True
            ).all()
            
            for zone in surge_zone:
                # Calcular distância simples
                distance = ((lat - zone.center_lat) ** 2 + (lng - zone.center_lng) ** 2) ** 0.5
                distance_km = distance * 111  # Conversão aproximada para km
                
                if distance_km <= zone.radius_km:
                    return zone.current_multiplier
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Erro ao obter surge zone: {e}")
            return 1.0  
        

    def _fetch_weather(self, lat: float, lng: float) -> dict:
        """Busca dados do clima via API"""
        try:
            # Substitua pela sua chave da OpenWeatherMap
            API_KEY = "your_openweather_api_key"
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": lat,
                "lon": lng,
                "appid": API_KEY,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=5)
            return response.json() if response.status_code == 200 else None
            
        except Exception as e:
            logger.error(f"Erro na API de clima: {e}")
            return None
        

    def _check_special_events(self, lat: float, lng: float) -> bool:
        """Verifica se há eventos especiais na região"""
        now = datetime.now()
        
        # Eventos conhecidos (exemplo)
        # Em produção, isso viria de um banco de dados ou API
        special_dates = {
            "2025-12-31": "Réveillon",
            "2025-06-15": "Rock in Rio", 
            # Adicionar mais eventos...
        }
        
        today = now.strftime("%Y-%m-%d")
        return today in special_dates
    

    def _generate_explanation(self, multiplier: float) -> str:
        """Gera explicação humana do preço"""
        if multiplier >= 2.0:
            return "Preço alto devido à grande demanda e poucos motoristas disponíveis"
        elif multiplier >= 1.5:
            return "Preço um pouco acima do normal devido à alta demanda"
        elif multiplier >= 1.2:
            return "Preço ligeiramente acima devido ao horário de movimento"
        elif multiplier <= 0.9:
            return "Preço promocional! Baixa demanda na região"
        else:
            return "Preço normal"