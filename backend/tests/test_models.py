"""
Unit tests for Pydantic models and validation.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from backend.models import (
    FuelTransaction,
    FuelTransactionCreate,
    Vehicle,
    VehicleCreate,
    VehicleUpdate,
    Project,
    Worker,
    AnomalyResult,
    User,
    UserCreate
)


@pytest.mark.unit
class TestFuelTransactionModel:
    """Test FuelTransaction model validation."""
    
    def test_valid_transaction(self):
        """Valid transaction data should pass validation."""
        tx = FuelTransactionCreate(
            transaction_id="TX001",
            provider="okq8",
            card_id="CARD123",
            vehicle_id="V001",
            timestamp=datetime.now(),
            liters=50.0,
            price_per_liter=20.5,
            total_amount=1025.0,
            fuel_type="Diesel",
            station_id="S001",
            station_lat=59.3293,
            station_lon=18.0686
        )
        assert tx.transaction_id == "TX001"
        assert tx.liters == 50.0
    
    def test_negative_liters_fails(self):
        """Negative liters should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            FuelTransactionCreate(
                transaction_id="TX001",
                provider="okq8",
                card_id="CARD123",
                vehicle_id="V001",
                timestamp=datetime.now(),
                liters=-10.0,  # Invalid
                price_per_liter=20.5,
                total_amount=1025.0,
                fuel_type="Diesel",
                station_id="S001",
                station_lat=59.3293,
                station_lon=18.0686
            )
        assert "greater than 0" in str(exc_info.value).lower()
    
    def test_invalid_latitude(self):
        """Invalid latitude should fail validation."""
        with pytest.raises(ValidationError):
            FuelTransactionCreate(
                transaction_id="TX001",
                provider="okq8",
                card_id="CARD123",
                vehicle_id="V001",
                timestamp=datetime.now(),
                liters=50.0,
                price_per_liter=20.5,
                total_amount=1025.0,
                fuel_type="Diesel",
                station_id="S001",
                station_lat=95.0,  # Invalid (>90)
                station_lon=18.0686
            )
    
    def test_invalid_provider(self):
        """Invalid provider should fail validation."""
        with pytest.raises(ValidationError):
            FuelTransactionCreate(
                transaction_id="TX001",
                provider="unknown_provider",  # Not in allowed list
                card_id="CARD123",
                vehicle_id="V001",
                timestamp=datetime.now(),
                liters=50.0,
                price_per_liter=20.5,
                total_amount=1025.0,
                fuel_type="Diesel",
                station_id="S001",
                station_lat=59.3293,
                station_lon=18.0686
            )


@pytest.mark.unit
class TestVehicleModel:
    """Test Vehicle model validation."""
    
    def test_valid_vehicle(self):
        """Valid vehicle data should pass validation."""
        vehicle = VehicleCreate(
            vehicle_id="V001",
            type="Excavator",
            tank_capacity_liters=200.0,
            reg_number="ABC-123",
            status="active"
        )
        assert vehicle.vehicle_id == "V001"
        assert vehicle.tank_capacity_liters == 200.0
    
    def test_negative_tank_capacity_fails(self):
        """Negative tank capacity should fail validation."""
        with pytest.raises(ValidationError):
            VehicleCreate(
                vehicle_id="V001",
                type="Excavator",
                tank_capacity_liters=-100.0,  # Invalid
                reg_number="ABC-123"
            )
    
    def test_vehicle_update_partial(self):
        """VehicleUpdate should allow partial updates."""
        update = VehicleUpdate(status="inactive")
        assert update.status == "inactive"
        assert update.type is None  # Not provided
    
    def test_invalid_status(self):
        """Invalid status should fail validation."""
        with pytest.raises(ValidationError):
            VehicleCreate(
                vehicle_id="V001",
                type="Truck",
                tank_capacity_liters=100.0,
                reg_number="ABC-123",
                status="broken"  # Not in allowed values
            )


@pytest.mark.unit
class TestProjectModel:
    """Test Project model validation."""
    
    def test_valid_project(self):
        """Valid project data should pass validation."""
        project = Project(
            project_id="P001",
            name="Test Project",
            geofence_lat=59.3293,
            geofence_lon=18.0686,
            geofence_radius_km=5.0,
            active=True
        )
        assert project.project_id == "P001"
        assert project.geofence_radius_km == 5.0
    
    def test_negative_radius_fails(self):
        """Negative geofence radius should fail validation."""
        with pytest.raises(ValidationError):
            Project(
                project_id="P001",
                name="Test Project",
                geofence_lat=59.3293,
                geofence_lon=18.0686,
                geofence_radius_km=-5.0,  # Invalid
                active=True
            )


@pytest.mark.unit
class TestWorkerModel:
    """Test Worker model validation."""
    
    def test_valid_worker(self):
        """Valid worker data should pass validation."""
        worker = Worker(
            worker_id="W001",
            name="John Doe",
            schedule_start="07:00",
            schedule_end="16:00",
            assigned_project_ids=["P001", "P002"]
        )
        assert worker.worker_id == "W001"
        assert len(worker.assigned_project_ids) == 2
    
    def test_invalid_time_format(self):
        """Invalid time format should fail validation."""
        with pytest.raises(ValidationError):
            Worker(
                worker_id="W001",
                name="John Doe",
                schedule_start="7:00",  # Missing leading zero
                schedule_end="16:00",
                assigned_project_ids=[]
            )


@pytest.mark.unit
class TestUserModel:
    """Test User model validation."""
    
    def test_valid_user_create(self):
        """Valid user creation data should pass validation."""
        user = UserCreate(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User",
            role="viewer"
        )
        assert user.email == "test@example.com"
        assert len(user.password) >= 8
    
    def test_short_password_fails(self):
        """Password shorter than 8 characters should fail."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="short",  # Too short
                role="viewer"
            )
    
    def test_invalid_email_format(self):
        """Invalid email format should fail validation."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email",  # Invalid format
                username="testuser",
                password="SecurePass123!",
                role="viewer"
            )
    
    def test_invalid_role(self):
        """Invalid role should fail validation."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="SecurePass123!",
                role="superuser"  # Not in allowed roles
            )


@pytest.mark.unit
class TestAnomalyResultModel:
    """Test AnomalyResult model validation."""
    
    def test_valid_anomaly_result(self):
        """Valid anomaly result should pass validation."""
        result = AnomalyResult(
            transaction_id="TX001",
            is_anomalous=True,
            severity="High",
            risk_score=65,
            reasons=["Tank capacity exceeded", "Out of hours"]
        )
        assert result.is_anomalous
        assert result.severity == "High"
        assert len(result.reasons) == 2
    
    def test_risk_score_bounds(self):
        """Risk score should be between 0 and 100."""
        with pytest.raises(ValidationError):
            AnomalyResult(
                transaction_id="TX001",
                is_anomalous=True,
                severity="Critical",
                risk_score=150,  # Too high
                reasons=["Test"]
            )
        
        with pytest.raises(ValidationError):
            AnomalyResult(
                transaction_id="TX001",
                is_anomalous=False,
                severity="Low",
                risk_score=-10,  # Too low
                reasons=[]
            )
    
    def test_invalid_severity(self):
        """Invalid severity level should fail validation."""
        with pytest.raises(ValidationError):
            AnomalyResult(
                transaction_id="TX001",
                is_anomalous=True,
                severity="Extreme",  # Not in allowed values
                risk_score=50,
                reasons=["Test"]
            )
