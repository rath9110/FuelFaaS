"""
Integration tests for vehicle API endpoints.
"""

import pytest
from httpx import AsyncClient

from backend.db_models import VehicleDB


@pytest.mark.api
@pytest.mark.asyncio
class TestVehicleEndpoints:
    """Test vehicle CRUD endpoints."""
    
    async def test_create_vehicle(self, client: AsyncClient, auth_headers: dict):
        """Should create a new vehicle."""
        response = await client.post(
            "/api/v1/vehicles/",
            headers=auth_headers,
            json={
                "vehicle_id": "V999",
                "type": "Truck",
                "tank_capacity_liters": 150.0,
                "reg_number": "XYZ-789",
                "status": "active"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["vehicle_id"] == "V999"
        assert data["type"] == "Truck"
    
    async def test_list_vehicles(self, client: AsyncClient, auth_headers: dict, test_vehicle: VehicleDB):
        """Should list all vehicles."""
        response = await client.get(
            "/api/v1/vehicles/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(v["vehicle_id"] == test_vehicle.vehicle_id for v in data)
    
    async def test_get_vehicle(self, client: AsyncClient, auth_headers: dict, test_vehicle: VehicleDB):
        """Should get specific vehicle by ID."""
        response = await client.get(
            f"/api/v1/vehicles/{test_vehicle.vehicle_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["vehicle_id"] == test_vehicle.vehicle_id
        assert data["type"] == test_vehicle.type
    
    async def test_get_nonexistent_vehicle(self, client: AsyncClient, auth_headers: dict):
        """Should return 404 for non-existent vehicle."""
        response = await client.get(
            "/api/v1/vehicles/NONEXISTENT",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_update_vehicle(self, client: AsyncClient, auth_headers: dict, test_vehicle: VehicleDB):
        """Should update vehicle information."""
        response = await client.patch(
            f"/api/v1/vehicles/{test_vehicle.vehicle_id}",
            headers=auth_headers,
            json={"status": "inactive"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"
    
    async def test_delete_vehicle(self, client: AsyncClient, auth_headers: dict, test_vehicle: VehicleDB):
        """Should delete a vehicle."""
        response = await client.delete(
            f"/api/v1/vehicles/{test_vehicle.vehicle_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = await client.get(
            f"/api/v1/vehicles/{test_vehicle.vehicle_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    async def test_filter_vehicles_by_status(self, client: AsyncClient, auth_headers: dict, vehicle_factory):
        """Should filter vehicles by status."""
        # Create vehicles with different statuses
        await vehicle_factory(vehicle_id="VACTIVE1", status="active")
        await vehicle_factory(vehicle_id="VINACTIVE1", status="inactive")
        
        response = await client.get(
            "/api/v1/vehicles/?status=active",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(v["status"] == "active" for v in data)
