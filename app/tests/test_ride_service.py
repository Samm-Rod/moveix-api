# test_ride_service.py

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

# Imports do seu código
from app.services.ride import (
    confirm_ride, calculator_fare, calculator_ride, get_rides_by_client,
    cancel_ride, start_ride, finish_ride, get_current_ride_by_client,
    rate_ride, get_available_rides, accept_ride_service, get_rides_by_driver,
    get_list_rate
)
from app.models.ride import Ride
from app.models.driver import Driver
from app.models.client import Client
from app.models.vehicle import Vehicle


class TestConfirmRide:
    """Testes para confirmar uma corrida"""
    
    @pytest.fixture
    def db_session(self):
        """Mock da sessão do banco"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def ride_data(self):
        """Dados de exemplo para uma corrida"""
        return {
            "client_id": 1,
            "driver_id": 2,
            "start_location": "Rua A, 123",
            "end_location": "Rua B, 456",
            "distance": 10.5,
            "duration": 25.0,
            "fare": 35.50
        }
    
    @pytest.fixture
    def current_client(self):
        """Cliente atual autenticado"""
        client = Mock()
        client.id = 1
        return {"user": client, "role": "client"}
    
    def test_confirm_ride_success(self, db_session, ride_data, current_client):
        """Testa confirmação bem-sucedida de uma corrida"""
        # Mock do cliente no banco
        db_client = Mock()
        db_client.id = 1
        db_session.query.return_value.filter_by.return_value.first.return_value = db_client
        
        # Mock do driver
        driver = Mock()
        driver.id = 2
        driver.vehicles = [Mock()]
        driver.vehicles[0].id = 1
        
        # Configurar query chain para driver
        driver_query = Mock()
        driver_query.filter_by.return_value.first.return_value = driver
        db_session.query.return_value = driver_query
        
        # Executa
        result = confirm_ride(ride_data, db_session, current_client)
        
        # Verificações
        assert result.client_id == 1
        assert result.driver_id == 2
        assert result.status == "disponível"
        assert driver.is_active == False
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()
    
    def test_confirm_ride_unauthorized_client(self, db_session, ride_data):
        """Testa erro quando cliente não autorizado tenta confirmar"""
        current_user = {"user": Mock(), "role": "client"}
        current_user["user"].id = 999  # ID diferente do ride_data
        
        with pytest.raises(HTTPException) as exc_info:
            confirm_ride(ride_data, db_session, current_user)
        
        assert exc_info.value.status_code == 403
        assert "cliente dono" in exc_info.value.detail.lower()
    
    def test_confirm_ride_client_not_found(self, db_session, ride_data, current_client):
        """Testa erro quando cliente não existe no banco"""
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            confirm_ride(ride_data, db_session, current_client)
        
        assert exc_info.value.status_code == 404
        assert "cliente não encontrado" in exc_info.value.detail.lower()
    
    def test_confirm_ride_driver_not_found(self, db_session, ride_data, current_client):
        """Testa erro quando motorista não existe ou não está disponível"""
        # Mock cliente existe
        db_client = Mock()
        db_session.query.return_value.filter_by.return_value.first.side_effect = [db_client, None]
        
        with pytest.raises(HTTPException) as exc_info:
            confirm_ride(ride_data, db_session, current_client)
        
        assert exc_info.value.status_code == 404
        assert "motorista não encontrado" in exc_info.value.detail.lower()


class TestCalculatorFare:
    """Testes para cálculo de tarifa"""
    
    @pytest.fixture
    def driver_normal(self):
        """Motorista com veículo normal"""
        driver = Mock()
        vehicle = Mock()
        vehicle.model = "sedan"
        driver.vehicles = [vehicle]
        return driver
    
    @pytest.fixture
    def driver_truck(self):
        """Motorista com caminhão"""
        driver = Mock()
        vehicle = Mock()
        vehicle.model = "truck"
        driver.vehicles = [vehicle]
        return driver
    
    def test_calculator_fare_normal_vehicle(self, driver_normal):
        """Testa cálculo de tarifa para veículo normal"""
        result = calculator_fare(driver_normal, 10.0, 30.0)
        
        # base_fare (5.00) + price_by_km (2.50 * 10) + price_by_min (0.50 * 30)
        expected = 5.00 + 25.00 + 15.00
        assert result == expected
    
    def test_calculator_fare_truck(self, driver_truck):
        """Testa cálculo de tarifa para caminhão"""
        result = calculator_fare(driver_truck, 10.0, 30.0)
        
        # base_fare (5.00) + price_by_km (3.50 * 10) + price_by_min (0.80 * 30)
        expected = 5.00 + 35.00 + 24.00
        assert result == expected
    
    def test_calculator_fare_no_vehicle(self):
        """Testa cálculo quando motorista não tem veículo"""
        driver = Mock()
        driver.vehicles = []
        
        result = calculator_fare(driver, 5.0, 15.0)
        
        # Deve usar tarifa normal
        expected = 5.00 + (2.50 * 5.0) + (0.50 * 15.0)
        assert result == expected


class TestCalculatorRide:
    """Testes para cálculo de rota"""
    
    @pytest.fixture
    def db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def current_client(self):
        return {"role": "client"}
    
    @pytest.fixture
    def mock_google_response(self):
        return {
            "status": "OK",
            "routes": [{
                "legs": [{
                    "start_address": "Rua A, 123, Cidade",
                    "end_address": "Rua B, 456, Cidade",
                    "distance": {"value": 10500},  # 10.5 km
                    "duration": {"value": 1800}    # 30 min
                }]
            }]
        }
    
    @pytest.fixture
    def mock_drivers(self):
        driver1 = Mock()
        driver1.id = 1
        driver1.name = "João"
        driver1.vehicles = [Mock()]
        driver1.vehicles[0].model = "sedan"
        driver1.vehicles[0].color = "azul"
        driver1.vehicles[0].plate = "ABC-1234"
        
        driver2 = Mock()
        driver2.id = 2
        driver2.name = "Maria"
        driver2.vehicles = [Mock()]
        driver2.vehicles[0].model = "truck"
        driver2.vehicles[0].color = "branco"
        driver2.vehicles[0].plate = "XYZ-5678"
        
        return [driver1, driver2]
    
    @pytest.mark.asyncio
    async def test_calculator_ride_success(self, db_session, current_client, mock_google_response, mock_drivers):
        """Testa cálculo de rota bem-sucedido"""
        # Mock da query de drivers
        db_session.query.return_value.filter.return_value.all.return_value = mock_drivers
        
        with patch('app.services.ride.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_google_response
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await calculator_ride("Rua A, 123", "Rua B, 456", db_session, current_client)
        
        # Verificações
        assert result["distance_km"] == 10.5
        assert result["duration_min"] == 30.0
        assert len(result["options"]) == 2
        assert result["options"][0]["driver_name"] == "João"
        assert result["options"][1]["driver_name"] == "Maria"
    
    @pytest.mark.asyncio
    async def test_calculator_ride_unauthorized_role(self, db_session):
        """Testa erro quando usuário não é cliente"""
        current_user = {"role": "driver"}
        
        with pytest.raises(HTTPException) as exc_info:
            await calculator_ride("origem", "destino", db_session, current_user)
        
        assert exc_info.value.status_code == 403
        assert "apenas clientes" in exc_info.value.detail.lower()
    
    @pytest.mark.asyncio
    async def test_calculator_ride_google_api_error(self, db_session, current_client):
        """Testa erro da API do Google"""
        mock_response = {"status": "NOT_FOUND"}
        
        with patch('app.services.ride.httpx.AsyncClient') as mock_client:
            mock_resp = Mock()
            mock_resp.json.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_resp
            
            with pytest.raises(HTTPException) as exc_info:
                await calculator_ride("origem", "destino", db_session, current_client)
        
        assert exc_info.value.status_code == 400
        assert "rota não encontrada" in exc_info.value.detail.lower()


class TestRideStatusOperations:
    """Testes para operações de status da corrida"""
    
    @pytest.fixture
    def db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_ride(self):
        ride = Mock()
        ride.id = 1
        ride.client_id = 1
        ride.driver_id = 2
        ride.status = "disponivel"
        ride.rating = None
        return ride
    
    def test_cancel_ride_by_client_success(self, db_session, mock_ride):
        """Testa cancelamento bem-sucedido pelo cliente"""
        db_session.query.return_value.filter.return_value.first.return_value = mock_ride
        
        result = cancel_ride(1, "client", 1, db_session)
        
        assert result.status == "cancelled"
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()
    
    def test_cancel_ride_unauthorized_client(self, db_session, mock_ride):
        """Testa erro quando cliente não autorizado tenta cancelar"""
        db_session.query.return_value.filter.return_value.first.return_value = mock_ride
        
        with pytest.raises(HTTPException) as exc_info:
            cancel_ride(999, "client", 1, db_session)
        
        assert exc_info.value.status_code == 403
        assert "não autorizado" in exc_info.value.detail.lower()
    
    def test_start_ride_success(self, db_session, mock_ride):
        """Testa início bem-sucedido da corrida"""
        db_session.query.return_value.filter_by.return_value.first.return_value = mock_ride
        
        result = start_ride(2, 1, db_session)
        
        assert result.status == "em_andamento"
        assert result.start_time is not None
        db_session.commit.assert_called_once()
    
    def test_start_ride_not_found(self, db_session):
        """Testa erro quando corrida não é encontrada para iniciar"""
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            start_ride(2, 999, db_session)
        
        assert exc_info.value.status_code == 404
    
    def test_finish_ride_success(self, db_session, mock_ride):
        """Testa finalização bem-sucedida da corrida"""
        mock_ride.status = "em_andamento"
        db_session.query.return_value.filter_by.return_value.first.return_value = mock_ride
        
        result = finish_ride(2, 1, db_session)
        
        assert result.status == "finalizada"
        assert result.end_time is not None
        db_session.commit.assert_called_once()


class TestRideRating:
    """Testes para avaliação de corridas"""
    
    @pytest.fixture
    def db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def finished_ride(self):
        ride = Mock()
        ride.id = 1
        ride.client_id = 1
        ride.status = "finalizada"
        ride.rating = None
        return ride
    
    def test_rate_ride_success(self, db_session, finished_ride):
        """Testa avaliação bem-sucedida"""
        db_session.query.return_value.filter_by.return_value.first.return_value = finished_ride
        
        result = rate_ride(1, 1, 5, db_session)
        
        assert result.rating == 5
        db_session.commit.assert_called_once()
    
    def test_rate_ride_not_finished(self, db_session, finished_ride):
        """Testa erro ao avaliar corrida não finalizada"""
        finished_ride.status = "em_andamento"
        db_session.query.return_value.filter_by.return_value.first.return_value = finished_ride
        
        with pytest.raises(HTTPException) as exc_info:
            rate_ride(1, 1, 5, db_session)
        
        assert exc_info.value.status_code == 400
        assert "finalizadas" in exc_info.value.detail.lower()
    
    def test_rate_ride_already_rated(self, db_session, finished_ride):
        """Testa erro ao avaliar corrida já avaliada"""
        finished_ride.rating = 4
        db_session.query.return_value.filter_by.return_value.first.return_value = finished_ride
        
        with pytest.raises(HTTPException) as exc_info:
            rate_ride(1, 1, 5, db_session)
        
        assert exc_info.value.status_code == 400
        assert "já foi avaliada" in exc_info.value.detail.lower()
    
    @pytest.mark.parametrize("rating", [-1, 6, 10])
    def test_rate_ride_invalid_rating(self, db_session, finished_ride, rating):
        """Testa erro com avaliação inválida"""
        db_session.query.return_value.filter_by.return_value.first.return_value = finished_ride
        
        with pytest.raises(HTTPException) as exc_info:
            rate_ride(1, 1, rating, db_session)
        
        assert exc_info.value.status_code == 400
        assert "entre 0 e 5" in exc_info.value.detail.lower()


class TestRideQueries:
    """Testes para consultas de corridas"""
    
    @pytest.fixture
    def db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_rides(self):
        rides = []
        for i in range(3):
            ride = Mock()
            ride.id = i + 1
            ride.client_id = 1
            ride.driver_id = 2
            ride.status = "finalizada" if i < 2 else "em_andamento"
            ride.rating = 5 if i < 2 else None
            rides.append(ride)
        return rides
    
    def test_get_rides_by_client(self, db_session, mock_rides):
        """Testa busca de corridas por cliente"""
        db_session.query.return_value.filter.return_value.all.return_value = mock_rides
        
        result = get_rides_by_client(1, db_session)
        
        assert len(result) == 3
        assert result == mock_rides
    
    def test_get_rides_by_driver(self, db_session, mock_rides):
        """Testa busca de corridas por motorista"""
        db_session.query.return_value.filter.return_value.all.return_value = mock_rides
        
        result = get_rides_by_driver(2, db_session)
        
        assert len(result) == 3
        assert result == mock_rides
    
    def test_get_available_rides(self, db_session):
        """Testa busca de corridas disponíveis"""
        available_rides = [Mock(), Mock()]
        db_session.query.return_value.filter.return_value.all.return_value = available_rides
        
        result = get_available_rides(db_session)
        
        assert len(result) == 2
        assert result == available_rides
    
    def test_get_current_ride_by_client(self, db_session):
        """Testa busca de corrida atual do cliente"""
        current_ride = Mock()
        current_ride.status = "em_andamento"
        
        query_mock = Mock()
        query_mock.filter.return_value.order_by.return_value.first.return_value = current_ride
        db_session.query.return_value = query_mock
        
        result = get_current_ride_by_client(1, db_session)
        
        assert result == current_ride
    
    def test_get_list_rate(self, db_session, mock_rides):
        """Testa listagem de avaliações do motorista"""
        rated_rides = [r for r in mock_rides if r.rating is not None]
        
        query_mock = Mock()
        query_mock.filter.return_value.all.return_value = rated_rides
        db_session.query.return_value = query_mock
        
        result = get_list_rate(2, db_session)
        
        assert len(result) == 2  # Apenas as com rating


class TestAcceptRide:
    """Testes para aceitar corrida"""
    
    @pytest.fixture
    def db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def driver_with_vehicle(self):
        driver = Mock()
        driver.id = 1
        driver.vehicles = [Mock()]
        driver.vehicles[0].id = 1
        return driver
    
    @pytest.fixture
    def available_ride(self):
        ride = Mock()
        ride.id = 1
        ride.status = "em_andamento"
        return ride
    
    def test_accept_ride_success(self, db_session, driver_with_vehicle, available_ride):
        """Testa aceitação bem-sucedida da corrida"""
        db_session.query.return_value.filter.return_value.first.return_value = available_ride
        
        result = accept_ride_service(driver_with_vehicle, 1, db_session)
        
        assert result.driver_id == 1
        assert result.vehicle_id == 1
        assert result.status == "em_andamento"
        assert result.start_time is not None
        db_session.commit.assert_called_once()
    
    def test_accept_ride_no_vehicle(self, db_session, available_ride):
        """Testa erro quando motorista não tem veículo"""
        driver = Mock()
        driver.vehicles = []
        
        db_session.query.return_value.filter.return_value.first.return_value = available_ride
        
        with pytest.raises(HTTPException) as exc_info:
            accept_ride_service(driver, 1, db_session)
        
        assert exc_info.value.status_code == 400
        assert "não tem veículo" in exc_info.value.detail.lower()
    
    def test_accept_ride_not_available(self, db_session, driver_with_vehicle):
        """Testa erro quando corrida não está disponível"""
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            accept_ride_service(driver_with_vehicle, 999, db_session)
        
        assert exc_info.value.status_code == 404
        assert "não disponível" in exc_info.value.detail.lower()


# Configuração pytest
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configuração automática para todos os testes"""
    # Aqui você pode configurar variáveis de ambiente ou mocks globais
    pass


# Executar os testes
if __name__ == "__main__":
    pytest.main([__file__, "-v"])