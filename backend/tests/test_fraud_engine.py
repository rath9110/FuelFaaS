"""
Unit tests for fraud detection engine and rules.
"""

import pytest
from datetime import datetime, timedelta
from backend import fraud_rules
from backend.engine import AnomalyEngine
from backend.models import FuelTransaction, Vehicle, Project, Worker


class TestHaversineDistance:
    """Test haversine distance calculation."""
    
    def test_same_location(self):
        """Distance between same coordinates should be 0."""
        distance = fraud_rules.haversine(18.0, 59.0, 18.0, 59.0)
        assert distance == 0.0
    
    def test_known_distance(self):
        """Test with known distance between Stockholm and Gothenburg."""
        # Stockholm: 59.3293, 18.0686
        # Gothenburg: 57.7089, 11.9746
        # Approximate distance: ~400km
        distance = fraud_rules.haversine(18.0686, 59.3293, 11.9746, 57.7089)
        assert 390 < distance < 410  # Allow some tolerance


@pytest.mark.fraud
class TestOutOfHoursRule:
    """Test out-of-hours fueling detection."""
    
    def test_within_default_hours(self):
        """Transaction during default working hours should pass."""
        tx_time = datetime(2025, 11, 24, 12, 0, 0)  # Noon
        is_violation, reason, score = fraud_rules.check_out_of_hours(
            tx_time, None, None
        )
        assert not is_violation
        assert score == 0
    
    def test_outside_default_hours_early(self):
        """Transaction too early should be flagged."""
        tx_time = datetime(2025, 11, 24, 5, 0, 0)  # 5 AM
        is_violation, reason, score = fraud_rules.check_out_of_hours(
            tx_time, None, None
        )
        assert is_violation
        assert score == 25
        assert "outside standard working hours" in reason.lower()
    
    def test_outside_default_hours_late(self):
        """Transaction too late should be flagged."""
        tx_time = datetime(2025, 11, 24, 20, 0, 0)  # 8 PM
        is_violation, reason, score = fraud_rules.check_out_of_hours(
            tx_time, None, None
        )
        assert is_violation
        assert score == 25
    
    def test_within_worker_schedule(self):
        """Transaction within worker schedule should pass."""
        tx_time = datetime(2025, 11, 24, 10, 0, 0)  # 10 AM
        is_violation, reason, score = fraud_rules.check_out_of_hours(
            tx_time, "07:00", "16:00"
        )
        assert not is_violation
        assert score == 0
    
    def test_outside_worker_schedule(self):
        """Transaction outside worker schedule should be flagged."""
        tx_time = datetime(2025, 11, 24, 18, 0, 0)  # 6 PM
        is_violation, reason, score = fraud_rules.check_out_of_hours(
            tx_time, "07:00", "16:00"
        )
        assert is_violation
        assert score == 30
        assert "07:00-16:00" in reason


@pytest.mark.fraud
class TestGeofenceRule:
    """Test geofence violation detection."""
    
    def test_within_geofence(self):
        """Station within geofence should pass."""
        is_violation, reason, score = fraud_rules.check_geofence_violation(
            59.33, 18.07,  # Near center
            59.3293, 18.0686,  # Center
            5.0,  # 5km radius
            "Test Project",
            15.0  # 15km buffer
        )
        assert not is_violation
        assert score == 0
    
    def test_outside_geofence(self):
        """Station far outside geofence should be flagged."""
        is_violation, reason, score = fraud_rules.check_geofence_violation(
            60.0, 19.0,  # ~100km away
            59.3293, 18.0686,
            5.0,
            "Test Project",
            15.0
        )
        assert is_violation
        assert score == 40
        assert "away from project" in reason.lower()
    
    def test_no_geofence_data(self):
        """Missing geofence data should not flag."""
        is_violation, reason, score = fraud_rules.check_geofence_violation(
            59.33, 18.07,
            None, None, None,
            "Test Project",
            15.0
        )
        assert not is_violation


@pytest.mark.fraud
class TestTankCapacityRule:
    """Test tank capacity violation detection."""
    
    def test_within_capacity(self):
        """Normal fuel amount should pass."""
        is_violation, reason, score = fraud_rules.check_tank_capacity_violation(
            50.0,  # 50 liters
            100.0  # 100L capacity
        )
        assert not is_violation
        assert score == 0
    
    def test_exceeds_capacity(self):
        """Fuel amount exceeding capacity should be flagged."""
        is_violation, reason, score = fraud_rules.check_tank_capacity_violation(
            150.0,  # 150 liters
            100.0  # 100L capacity
        )
        assert is_violation
        assert score == 40
        assert "exceeds tank capacity" in reason.lower()
    
    def test_tolerance_allowed(self):
        """5% tolerance should be allowed."""
        is_violation, reason, score = fraud_rules.check_tank_capacity_violation(
            104.0,  # 4% over
            100.0
        )
        assert not is_violation


@pytest.mark.fraud
class TestDoubleDippingRule:
    """Test double-dipping detection."""
    
    def test_no_recent_transactions(self):
        """No recent transactions should pass."""
        tx_time = datetime(2025, 11, 24, 12, 0, 0)
        is_violation, reason, score = fraud_rules.check_double_dipping(
            tx_time, [], 30
        )
        assert not is_violation
    
    def test_recent_transaction_within_threshold(self):
        """Transaction within 30 minutes should be flagged."""
        tx_time = datetime(2025, 11, 24, 12, 0, 0)
        recent = [datetime(2025, 11, 24, 11, 45, 0)]  # 15 min ago
        is_violation, reason, score = fraud_rules.check_double_dipping(
            tx_time, recent, 30
        )
        assert is_violation
        assert score == 35
        assert "double-dipping" in reason.lower()
    
    def test_old_transaction_outside_threshold(self):
        """Transaction older than threshold should pass."""
        tx_time = datetime(2025, 11, 24, 12, 0, 0)
        recent = [datetime(2025, 11, 24, 11, 0, 0)]  # 60 min ago
        is_violation, reason, score = fraud_rules.check_double_dipping(
            tx_time, recent, 30
        )
        assert not is_violation


@pytest.mark.fraud
class TestPriceAnomalyRule:
    """Test fuel price anomaly detection."""
    
    def test_normal_price(self):
        """Normal price should pass."""
        is_violation, reason, score = fraud_rules.check_price_anomaly(
            18.5,  # Close to market average
            18.0,
            20.0  # 20% threshold
        )
        assert not is_violation
    
    def test_price_too_high(self):
        """Excessively high price should be flagged."""
        is_violation, reason, score = fraud_rules.check_price_anomaly(
            25.0,  # 38% above market
            18.0,
            20.0
        )
        assert is_violation
        assert score == 20
        assert "above market" in reason.lower()
    
    def test_price_too_low(self):
        """Suspiciously low price should be flagged."""
        is_violation, reason, score = fraud_rules.check_price_anomaly(
            10.0,  # 44% below market
            18.0,
            20.0
        )
        assert is_violation
        assert score == 30
        assert "below market" in reason.lower()


@pytest.mark.fraud
class TestWeekendHolidayRule:
    """Test weekend/holiday detection."""
    
    def test_weekday(self):
        """Weekday transaction should pass."""
        tx_time = datetime(2025, 11, 24, 12, 0, 0)  # Monday
        is_violation, reason, score = fraud_rules.check_weekend_holiday(
            tx_time, None
        )
        assert not is_violation
    
    def test_saturday(self):
        """Saturday transaction should be flagged."""
        tx_time = datetime(2025, 11, 29, 12, 0, 0)  # Saturday
        is_violation, reason, score = fraud_rules.check_weekend_holiday(
            tx_time, None
        )
        assert is_violation
        assert score == 20
        assert "weekend" in reason.lower()
    
    def test_sunday(self):
        """Sunday transaction should be flagged."""
        tx_time = datetime(2025, 11, 30, 12, 0, 0)  # Sunday
        is_violation, reason, score = fraud_rules.check_weekend_holiday(
            tx_time, None
        )
        assert is_violation
        assert "weekend" in reason.lower()


@pytest.mark.fraud
class TestImpossibleTravelRule:
    """Test impossible travel detection."""
    
    def test_no_previous_location(self):
        """No previous transaction data should pass."""
        current_time = datetime(2025, 11, 24, 12, 0, 0)
        is_violation, reason, score = fraud_rules.check_consecutive_locations(
            59.33, 18.07,
            current_time,
            None, None, None,
            120.0
        )
        assert not is_violation
    
    def test_reasonable_travel(self):
        """Reasonable travel distance/time should pass."""
        current_time = datetime(2025, 11, 24, 12, 0, 0)
        previous_time = datetime(2025, 11, 24, 11, 0, 0)  # 1 hour ago
        # ~50km distance, 1 hour = 50km/h average (reasonable)
        is_violation, reason, score = fraud_rules.check_consecutive_locations(
            59.8, 18.0,
            current_time,
            59.3, 18.0,
            previous_time,
            120.0
        )
        assert not is_violation
    
    def test_impossible_travel(self):
        """Impossible travel speed should be flagged."""
        current_time = datetime(2025, 11, 24, 12, 0, 0)
        previous_time = datetime(2025, 11, 24, 11, 45, 0)  # 15 min ago
        # ~50km distance, 15 min = 200km/h (impossible)
        is_violation, reason, score = fraud_rules.check_consecutive_locations(
            59.8, 18.0,
            current_time,
            59.3, 18.0,
            previous_time,
            120.0
        )
        assert is_violation
        assert score == 35
        assert "impossible travel" in reason.lower()


@pytest.mark.fraud
@pytest.mark.asyncio
class TestAnomalyEngine:
    """Test full anomaly engine integration."""
    
    async def test_clean_transaction(self):
        """Normal transaction should have low/no risk."""
        vehicles = {
            "V001": Vehicle(
                vehicle_id="V001",
                type="Truck",
                tank_capacity_liters=100.0,
                reg_number="ABC-123",
                status="active"
            )
        }
        
        engine = AnomalyEngine(vehicles, {}, {})
        
        transaction = FuelTransaction(
            transaction_id="TX001",
            provider="okq8",
            card_id="CARD123",
            vehicle_id="V001",
            timestamp=datetime(2025, 11, 24, 12, 0, 0),  # Weekday noon
            liters=50.0,
            price_per_liter=18.5,
            total_amount=925.0,
            fuel_type="Diesel",
            station_id="S001",
            station_lat=59.33,
            station_lon=18.07
        )
        
        result = await engine.check_transaction(transaction)
        
        assert result.transaction_id == "TX001"
        assert result.risk_score < 21  # Should be low risk
        assert not result.is_anomalous
    
    async def test_multiple_violations(self):
        """Transaction with multiple violations should have high risk."""
        vehicles = {
            "V001": Vehicle(
                vehicle_id="V001",
                type="Truck",
                tank_capacity_liters=50.0,  # Small tank
                reg_number="ABC-123",
                status="inactive"  # Inactive!
            )
        }
        
        engine = AnomalyEngine(vehicles, {}, {})
        
        transaction = FuelTransaction(
            transaction_id="TX002",
            provider="okq8",
            card_id="CARD123",
            vehicle_id="V001",
            timestamp=datetime(2025, 11, 30, 3, 0, 0),  # Sunday, 3 AM
            liters=100.0,  # Exceeds capacity!
            price_per_liter=30.0,  # High price
            total_amount=3000.0,
            fuel_type="Diesel",
            station_id="S001",
            station_lat=59.33,
            station_lon=18.07
        )
        
        result = await engine.check_transaction(transaction)
        
        assert result.is_anomalous
        assert result.risk_score > 70  # Multiple violations
        assert result.severity in ["High", "Critical"]
        assert len(result.reasons) >= 3  # Should have multiple reasons
