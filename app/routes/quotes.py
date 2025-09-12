# app/routes/quotes.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.ride import RideQuoteResponse
from app.services.ride import calculator_ride
from app.schemas.quote import DynamicQuoteResponse
from app.services.dynamic_pricing import DynamicPricingService
from app.auth.dependencies import get_current_user
import logging

router = APIRouter(prefix="/api/v1")

@router.get('/', response_model=RideQuoteResponse)
async def calculate_quote(
    origin: str = Query(..., description="Endereço de partida"),
    destination: str = Query(..., description="Endereço de destino"),
    freight_type: str = Query("standard", description="Tipo de frete"),
    volume_m3: float = Query(5.0, description="Volume em m³"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calcular orçamento de frete"""
    return await calculator_ride(origin, destination, db, current_user)


router = APIRouter(prefix="/quotes", tags=["Quotes"])
logger = logging.getLogger(__name__)

@router.get("/calculate", response_model=DynamicQuoteResponse)
async def calculate_dynamic_quote(
    origin_lat: float = Query(..., description="Latitude da origem"),
    origin_lng: float = Query(..., description="Longitude da origem"),
    dest_lat: float = Query(..., description="Latitude do destino"),
    dest_lng: float = Query(..., description="Longitude do destino"),
    freight_type: str = Query("standard", description="Tipo de frete"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calcular cotação com preço dinâmico"""
    
    try:
        # Calcular distância e tempo (usar Google Maps API)
        distance_km, duration_minutes = await calculate_route(
            origin_lat, origin_lng, dest_lat, dest_lng
        )
        
        # Aplicar precificação dinâmica
        pricing_service = DynamicPricingService(db)
        pricing_result = pricing_service.calculate_dynamic_price(
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            freight_type=freight_type
        )
        
        # Log para analytics
        logger.info(f"Dynamic pricing - User: {current_user['user_id']}, "
                   f"Multiplier: {pricing_result['multiplier']}, "
                   f"Price: {pricing_result['final_price']}")
        
        return DynamicQuoteResponse(
            base_price=pricing_result["base_price"],
            final_price=pricing_result["final_price"],
            surge_multiplier=pricing_result["multiplier"],
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            breakdown=pricing_result["breakdown"],
            explanation=pricing_result["explanation"],
            valid_until=pricing_result["valid_until"],
            freight_type=freight_type
        )
        
    except Exception as e:
        logger.error(f"Erro no cálculo dinâmico: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro no cálculo de preço")

async def calculate_route(origin_lat: float, origin_lng: float, 
                         dest_lat: float, dest_lng: float) -> tuple:
    """Calcular rota usando Google Maps API"""
    # Implementação da integração com Google Maps
    # Por enquanto, cálculo aproximado
    
    import math
    
    # Distância em linha reta (Haversine)
    def haversine_distance(lat1, lng1, lat2, lng2):
        R = 6371  # Raio da Terra em km
        
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    distance = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    
    # Estimativa de tempo (assumindo 40 km/h média)
    duration = (distance / 40) * 60  # minutos
    
    return distance * 1.3, duration  # 1.3x para compensar não ser linha reta