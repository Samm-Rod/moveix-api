# Sistema de Precificação Dinâmica baseado em Demanda
from datetime import datetime, timedelta
from typing import Dict, List
import math


class DynamicPricingByDemand:
    def __init__(self):
        # Configurações base
        self.base_surge_threshold = 1.5  # Quando começar a aplicar surge
        self.max_surge_multiplier = 3.0  # Máximo de 3x o preço normal
        self.min_surge_multiplier = 1.0  # Mínimo sempre 1x

        # Janelas de tempo para análise
        self.analysis_windows = {
            'immediate': 15,  # últimos 15 min
            'short': 60,  # última 1h
            'medium': 180,  # últimas 3h
            'long': 720  # últimas 12h
        }

    def calculate_demand_metrics(self, region: str, current_time: datetime) -> Dict:
        """Calcula métricas de demanda para diferentes janelas de tempo"""

        metrics = {}

        for window_name, minutes in self.analysis_windows.items():
            start_time = current_time - timedelta(minutes=minutes)

            # Simular busca no banco de dados
            requests_count = self._get_requests_count(region, start_time, current_time)
            completed_rides = self._get_completed_rides(region, start_time, current_time)
            available_drivers = self._get_available_drivers(region, current_time)

            # Métricas calculadas
            metrics[window_name] = {
                'total_requests': requests_count,
                'completed_rides': completed_rides,
                'available_drivers': available_drivers,
                'requests_per_hour': (requests_count / minutes) * 60,
                'completion_rate': completed_rides / max(requests_count, 1),
                'demand_supply_ratio': requests_count / max(available_drivers, 1)
            }

        return metrics

    def calculate_surge_multiplier(self, region: str, current_time: datetime) -> float:
        """Calcula o multiplicador de surge baseado na demanda"""

        metrics = self.calculate_demand_metrics(region, current_time)

        # Pesos para cada janela temporal (mais recente = mais peso)
        weights = {
            'immediate': 0.5,  # 50% - mais importante
            'short': 0.3,  # 30%
            'medium': 0.15,  # 15%
            'long': 0.05  # 5% - contexto histórico
        }

        # Calcula surge para cada janela
        surge_factors = {}
        for window, weight in weights.items():
            window_metrics = metrics[window]

            # Fator principal: razão demanda/oferta
            demand_ratio = window_metrics['demand_supply_ratio']

            # Fator secundário: taxa de completion baixa = alta demanda não atendida
            completion_penalty = 1 + (1 - window_metrics['completion_rate'])

            # Fórmula do surge para esta janela
            if demand_ratio >= self.base_surge_threshold:
                window_surge = min(
                    self.max_surge_multiplier,
                    1.0 + (demand_ratio - 1.0) * 0.4 * completion_penalty
                )
            else:
                window_surge = 1.0

            surge_factors[window] = window_surge

        # Média ponderada dos surges
        final_surge = sum(
            surge_factors[window] * weights[window]
            for window in weights.keys()
        )

        # Garantir limites
        final_surge = max(self.min_surge_multiplier,
                          min(self.max_surge_multiplier, final_surge))

        return round(final_surge, 1)  # Arredondar para 1 casa decimal

    def get_surge_explanation(self, surge_multiplier: float, region: str) -> str:
        """Retorna explicação amigável do surge para o usuário"""

        if surge_multiplier == 1.0:
            return "Preço normal"
        elif surge_multiplier <= 1.3:
            return f"Demanda ligeiramente alta (+{int((surge_multiplier - 1) * 100)}%)"
        elif surge_multiplier <= 1.8:
            return f"Alta demanda (+{int((surge_multiplier - 1) * 100)}%)"
        elif surge_multiplier <= 2.5:
            return f"Demanda muito alta (+{int((surge_multiplier - 1) * 100)}%)"
        else:
            return f"Demanda extrema (+{int((surge_multiplier - 1) * 100)}%)"

    def calculate_final_price(self, base_price: float, region: str,
                              current_time: datetime) -> Dict:
        """Calcula preço final com surge aplicado"""

        surge_multiplier = self.calculate_surge_multiplier(region, current_time)
        final_price = base_price * surge_multiplier

        return {
            'base_price': base_price,
            'surge_multiplier': surge_multiplier,
            'final_price': round(final_price, 2),
            'surge_explanation': self.get_surge_explanation(surge_multiplier, region),
            'savings_if_wait': self._estimate_savings_if_wait(base_price, region, current_time)
        }

    def _estimate_savings_if_wait(self, base_price: float, region: str,
                                  current_time: datetime) -> Dict:
        """Estima economias se esperar"""

        # Simular previsão para próximas horas
        predictions = {}
        for hours_ahead in [1, 2, 3, 6]:
            future_time = current_time + timedelta(hours=hours_ahead)
            future_surge = self.calculate_surge_multiplier(region, future_time)
            future_price = base_price * future_surge

            savings = (base_price * self.calculate_surge_multiplier(region, current_time)) - future_price

            if savings > 0:
                predictions[f"{hours_ahead}h"] = {
                    'estimated_price': round(future_price, 2),
                    'estimated_savings': round(savings, 2),
                    'surge_multiplier': future_surge
                }

        return predictions if predictions else {"message": "Preços devem se manter similares"}

    # Métodos simulados - substituir pela sua lógica de banco de dados
    def _get_requests_count(self, region: str, start_time: datetime, end_time: datetime) -> int:
        """Simula busca de pedidos no banco"""
        # Aqui você faria: SELECT COUNT(*) FROM ride_requests WHERE region=? AND created_at BETWEEN ? AND ?
        return 25  # Exemplo

    def _get_completed_rides(self, region: str, start_time: datetime, end_time: datetime) -> int:
        """Simula busca de corridas completadas"""
        # SELECT COUNT(*) FROM rides WHERE region=? AND completed_at BETWEEN ? AND ?
        return 18  # Exemplo

    def _get_available_drivers(self, region: str, current_time: datetime) -> int:
        """Simula busca de motoristas disponíveis"""
        # SELECT COUNT(*) FROM drivers WHERE region=? AND status='available' AND last_ping > ?
        return 12  # Exemplo


# ===== EXEMPLO DE USO =====
if __name__ == "__main__":
    pricing = DynamicPricingByDemand()

    # Cenário de teste
    base_price = 150.00  # R$ 150 base
    region = "centro_sao_paulo"
    current_time = datetime.now()

    # Calcular preço com surge
    result = pricing.calculate_final_price(base_price, region, current_time)

    print("=== RESULTADO DA PRECIFICAÇÃO ===")
    print(f"Preço base: R$ {result['base_price']:.2f}")
    print(f"Multiplicador surge: {result['surge_multiplier']}x")
    print(f"Preço final: R$ {result['final_price']:.2f}")
    print(f"Status: {result['surge_explanation']}")

    if result['savings_if_wait']:
        print("\n=== ECONOMIAS POSSÍVEIS ===")
        for time_period, info in result['savings_if_wait'].items():
            if isinstance(info, dict):
                print(f"Em {time_period}: R$ {info['estimated_price']:.2f} "
                      f"(economia de R$ {info['estimated_savings']:.2f})")

# ===== INTEGRAÇÃO COM FASTAPI =====
"""
@app.get("/pricing/calculate")
async def calculate_dynamic_pricing(
    base_price: float,
    region: str,
    pickup_lat: float,
    pickup_lng: float
):
    pricing_system = DynamicPricingByDemand()

    result = pricing_system.calculate_final_price(
        base_price=base_price,
        region=region,
        current_time=datetime.now()
    )

    return {
        "success": True,
        "pricing": result,
        "timestamp": datetime.now().isoformat()
    }
"""