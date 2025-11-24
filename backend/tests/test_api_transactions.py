"""
Integration tests for transaction and anomaly detection endpoints.
"""

import pytest
from datetime import datetime
from httpx import AsyncClient

from backend.db_models import VehicleDB, ProjectDB, TransactionDB


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.asyncio
class TestTransactionEndpoints:
    """Test transaction ingestion and anomaly detection."""
    
    async def test_ingest_clean_transaction(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_vehicle: VehicleDB,
        test_project: ProjectDB
    ):
        """Should ingest transaction and detect no anomalies."""
        response = await client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "transaction_id": "TXCLEAN001",
                "provider": "okq8",
                "card_id": "CARD123",
                "vehicle_id": test_vehicle.vehicle_id,
                "timestamp": "2025-11-25T12:00:00",  # Monday noon
                "liters": 50.0,
                "price_per_liter": 18.5,
                "total_amount": 925.0,
                "fuel_type": "Diesel",
                "station_id": "S001",
                "station_lat": 59.33,  # Near project
                "station_lon": 18.07
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["transaction_id"] == "TXCLEAN001"
        assert data["risk_score"] < 30  # Should be low risk
        assert not data["is_anomalous"]
    
    async def test_ingest_anomalous_transaction(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_vehicle: VehicleDB
    ):
        """Should detect anomalies in suspicious transaction."""
        response = await client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "transaction_id": "TXANOM001",
                "provider": "shell",
                "card_id": "CARD123",
                "vehicle_id": test_vehicle.vehicle_id,
                "timestamp": "2025-11-30T03:00:00",  # Sunday 3 AM
                "liters": 250.0,  # Exceeds tank capacity
                "price_per_liter": 35.0,  # High price
                "total_amount": 8750.0,
                "fuel_type": "Diesel",
                "station_id": "S999",
                "station_lat": 61.0,  # Far away
                "station_lon": 20.0
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_anomalous"]
        assert data["risk_score"] > 60  # Multiple violations
        assert data["severity"] in ["High", "Critical"]
        assert len(data["reasons"]) >= 2  # Multiple reasons
    
    async def test_list_transactions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: TransactionDB
    ):
        """Should list all transactions."""
        response = await client.get(
            "/api/v1/transactions/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_filter_transactions_by_vehicle(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_vehicle: VehicleDB,
        transaction_factory
    ):
        """Should filter transactions by vehicle."""
        # Create transactions for specific vehicle
        await transaction_factory(vehicle_id=test_vehicle.vehicle_id, transaction_id="TXVEH1")
        await transaction_factory(vehicle_id="VOTHER", transaction_id="TXVEH2")
        
        response = await client.get(
            f"/api/v1/transactions/?vehicle_id={test_vehicle.vehicle_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(tx["vehicle_id"] == test_vehicle.vehicle_id for tx in data)
    
    async def test_get_transaction(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction: TransactionDB
    ):
        """Should get specific transaction."""
        response = await client.get(
            f"/api/v1/transactions/{test_transaction.transaction_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == test_transaction.transaction_id


@pytest.mark.api
@pytest.mark.asyncio
class TestAnomalyEndpoints:
    """Test anomaly management endpoints."""
    
    async def test_list_anomalies(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_anomaly
    ):
        """Should list detected anomalies."""
        response = await client.get(
            "/api/v1/anomalies/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_filter_anomalies_by_severity(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_anomaly
    ):
        """Should filter anomalies by severity."""
        response = await client.get(
            "/api/v1/anomalies/?severity=High",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(a["severity"] == "High" for a in data)
    
    async def test_review_anomaly(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_anomaly
    ):
        """Should allow reviewing an anomaly."""
        response = await client.patch(
            f"/api/v1/anomalies/{test_anomaly.id}",
            headers=auth_headers,
            json={
                "reviewed": True,
                "status": "confirmed",
                "review_notes": "Confirmed fraud case"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["reviewed"] is True
        assert data["status"] == "confirmed"
        assert data["review_notes"] == "Confirmed fraud case"


@pytest.mark.api
@pytest.mark.asyncio
class TestStatsEndpoints:
    """Test statistics endpoints."""
    
    async def test_get_stats(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_transaction,
        test_anomaly
    ):
        """Should return dashboard statistics."""
        response = await client.get(
            "/api/v1/stats/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_transactions" in data
        assert "total_anomalies" in data
        assert "average_risk_score" in data
        assert "critical_anomalies" in data
        assert "high_anomalies" in data
        assert data["total_transactions"] >= 1
        assert data["total_anomalies"] >= 1
