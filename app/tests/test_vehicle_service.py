import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.vehicle import (
    create_vehicle, get_all_vehicles, update_vehicle, 
    delete_vehicle, choose_vehicle
)
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.models.vehicle import Vehicle
from app.models.driver import Driver

# Fixtures para reutilização
@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def driver():
    driver = Mock(spec=Driver)
    driver.id = 1
    return driver

@pytest.fixture
def vehicle_data():
    return VehicleCreate(
        model="Corolla",
        brand="Toyota", 
        plate="ABC-1234",
        color="Preto",
        license_category="B",
        size="médio"
    )

class TestCreateVehicle:
    def test_create_vehicle_success(self, mock_db, driver, vehicle_data):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = create_vehicle(vehicle_data, driver.id, mock_db)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result.model == vehicle_data.model

    def test_create_vehicle_duplicate_plate(self, mock_db, driver, vehicle_data):
        mock_db.query.return_value.filter.return_value.first.return_value = Vehicle()
        
        with pytest.raises(HTTPException) as exc_info:
            create_vehicle(vehicle_data, driver.id, mock_db)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail)

class TestGetAllVehicles:
    def test_get_all_vehicles_success(self, mock_db, driver):
        vehicles = [Vehicle(), Vehicle()]
        mock_db.query.return_value.filter.return_value.first.return_value = driver
        mock_db.query.return_value.filter.return_value.all.return_value = vehicles
        
        result = get_all_vehicles(driver, mock_db)
        
        assert len(result) == 2
        assert isinstance(result[0], Vehicle)

    def test_get_all_vehicles_driver_not_found(self, mock_db, driver):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_all_vehicles(driver, mock_db)
        
        assert exc_info.value.status_code == 404

class TestUpdateVehicle:
    @pytest.fixture
    def update_data(self):
        return VehicleUpdate(color="Branco", model="Corolla 2021")

    def test_update_vehicle_success(self, mock_db, driver, update_data):
        vehicle = Mock(spec=Vehicle)
        vehicle.id = 1
        vehicle.driver_id = driver.id
        mock_db.query.return_value.filter.return_value.first.return_value = vehicle
        
        result = update_vehicle(1, update_data, driver.id, mock_db)
        
        assert hasattr(vehicle, 'color')
        mock_db.commit.assert_called_once()
        assert result == vehicle

    def test_update_vehicle_not_found(self, mock_db, driver, update_data):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            update_vehicle(1, update_data, driver.id, mock_db)
        
        assert exc_info.value.status_code == 404

    def test_update_vehicle_wrong_owner(self, mock_db, driver, update_data):
        vehicle = Mock(spec=Vehicle)
        vehicle.driver_id = 2  # ID diferente
        mock_db.query.return_value.filter.return_value.first.return_value = vehicle
        
        with pytest.raises(HTTPException) as exc_info:
            update_vehicle(1, update_data, driver.id, mock_db)
        
        assert exc_info.value.status_code == 403

class TestDeleteVehicle:
    def test_delete_vehicle_success(self, mock_db, driver):
        vehicle = Mock(spec=Vehicle)
        vehicle.driver_id = driver.id
        mock_db.query.return_value.filter.return_value.first.return_value = vehicle
        
        result = delete_vehicle(1, driver.id, mock_db)
        
        mock_db.delete.assert_called_once_with(vehicle)
        mock_db.commit.assert_called_once()
        assert result == {'message': 'Vehicle removed successfully'}

    def test_delete_vehicle_not_found(self, mock_db, driver):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            delete_vehicle(1, driver.id, mock_db)
        
        assert exc_info.value.status_code == 404

class TestChooseVehicle:
    def test_choose_vehicle_success(self, mock_db, driver):
        vehicle = Mock(spec=Vehicle)
        vehicle.driver_id = driver.id
        mock_db.query.return_value.filter.return_value.first.return_value = vehicle
        
        result = choose_vehicle(1, driver.id, mock_db)
        
        assert result == vehicle

    def test_choose_vehicle_not_found(self, mock_db, driver):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            choose_vehicle(1, driver.id, mock_db)
        
        assert exc_info.value.status_code == 404

    def test_choose_vehicle_wrong_owner(self, mock_db, driver):
        vehicle = Mock(spec=Vehicle)
        vehicle.driver_id = 2
        mock_db.query.return_value.filter.return_value.first.return_value = vehicle
        
        with pytest.raises(HTTPException) as exc_info:
            choose_vehicle(1, driver.id, mock_db)
        
        assert exc_info.value.status_code == 403