from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from .models import FuelTransaction, Vehicle, Project, Worker, AnomalyResult
from .db_models import TransactionDB
from . import fraud_rules
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)


class AnomalyEngine:
    """
    Enhanced anomaly detection engine with comprehensive fraud detection rules.
    """
    
    def __init__(
        self,
        vehicles: Dict[str, Vehicle],
        projects: Dict[str, Project],
        workers: Dict[str, Worker],
        db_session: Optional[AsyncSession] = None
    ):
        self.vehicles = vehicles
        self.projects = projects
        self.workers = workers
        self.db_session = db_session
    
    async def get_recent_transactions(
        self,
        vehicle_id: str,
        since: datetime,
        exclude_transaction_id: Optional[str] = None
    ) -> List[TransactionDB]:
        """
        Get recent transactions for a vehicle from database.
        
        Args:
            vehicle_id: Vehicle ID
            since: Get transactions since this time
            exclude_transaction_id: Exclude this transaction ID from results
        
        Returns:
            List of recent transactions
        """
        if not self.db_session:
            return []
        
        query = select(TransactionDB).where(
            and_(
                TransactionDB.vehicle_id == vehicle_id,
                TransactionDB.timestamp >= since
            )
        )
        
        if exclude_transaction_id:
            query = query.where(TransactionDB.transaction_id != exclude_transaction_id)
        
        result = await self.db_session.execute(query.order_by(TransactionDB.timestamp.desc()))
        return result.scalars().all()
    
    async def check_transaction(self, transaction: FuelTransaction) -> AnomalyResult:
        """
        Analyze a fuel transaction for anomalies using all fraud detection rules.
        
        Args:
            transaction: Fuel transaction to analyze
        
        Returns:
            Anomaly detection result with risk score and reasons
        """
        reasons = []
        score = 0
        
        # Get related entities
        vehicle = self.vehicles.get(transaction.vehicle_id)
        project = None
        worker = None
        
        if vehicle and vehicle.assigned_to_project:
            project = self.projects.get(vehicle.assigned_to_project)
        
        if transaction.driver_id:
            worker = self.workers.get(transaction.driver_id)
        
        # Rule 1: Out-of-Hours Fueling
        is_violation, reason, rule_score = fraud_rules.check_out_of_hours(
            transaction.timestamp,
            worker.schedule_start if worker else None,
            worker.schedule_end if worker else None
        )
        if is_violation:
            reasons.append(reason)
            score += rule_score
        
        # Rule 2: Outside Project Geofence
        is_violation, reason, rule_score = fraud_rules.check_geofence_violation(
            transaction.station_lat,
            transaction.station_lon,
            project.geofence_lat if project else None,
            project.geofence_lon if project else None,
            project.geofence_radius_km if project else None,
            project.name if project else None,
            settings.geofence_buffer_km
        )
        if is_violation:
            reasons.append(reason)
            score += rule_score
        
        # Rule 3: Impossible Fuel Volume
        is_violation, reason, rule_score = fraud_rules.check_tank_capacity_violation(
            transaction.liters,
            vehicle.tank_capacity_liters if vehicle else None
        )
        if is_violation:
            reasons.append(reason)
            score += rule_score
        
        # Rule 4: Vehicle Inactive Status
        is_violation, reason, rule_score = fraud_rules.check_vehicle_inactive(
            vehicle.status if vehicle else None
        )
        if is_violation:
            reasons.append(reason)
            score += rule_score
        
        # Rule 5: Double-Dipping (requires database)
        if self.db_session:
            lookback_time = transaction.timestamp - timedelta(minutes=settings.double_dip_minutes)
            recent_txs = await self.get_recent_transactions(
                transaction.vehicle_id,
                lookback_time,
                transaction.transaction_id
            )
            recent_times = [tx.timestamp for tx in recent_txs]
            
            is_violation, reason, rule_score = fraud_rules.check_double_dipping(
                transaction.timestamp,
                recent_times,
                settings.double_dip_minutes
            )
            if is_violation:
                reasons.append(reason)
                score += rule_score
            
            # Rule 6: Price Anomaly
            # Could calculate market average from recent transactions
            # For now, using default market estimate
            is_violation, reason, rule_score = fraud_rules.check_price_anomaly(
                transaction.price_per_liter,
                None,  # Market average - could be calculated
                settings.price_anomaly_threshold_percent
            )
            if is_violation:
                reasons.append(reason)
                score += rule_score
            
            # Rule 7: Transaction Frequency
            day_start = transaction.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_txs = await self.get_recent_transactions(
                transaction.vehicle_id,
                day_start,
                transaction.transaction_id
            )
            daily_times = [tx.timestamp for tx in daily_txs]
            
            is_violation, reason, rule_score = fraud_rules.check_transaction_frequency(
                transaction.timestamp,
                daily_times,
                settings.max_transactions_per_day_per_vehicle
            )
            if is_violation:
                reasons.append(reason)
                score += rule_score
            
            # Rule 8: Weekend/Holiday Check
            is_violation, reason, rule_score = fraud_rules.check_weekend_holiday(
                transaction.timestamp,
                None  # Could load holidays from config/database
            )
            if is_violation:
                reasons.append(reason)
                score += rule_score
            
            # Rule 9: Consecutive Locations (impossible travel)
            if recent_txs:
                latest_tx = recent_txs[0]
                is_violation, reason, rule_score = fraud_rules.check_consecutive_locations(
                    transaction.station_lat,
                    transaction.station_lon,
                    transaction.timestamp,
                    latest_tx.station_lat,
                    latest_tx.station_lon,
                    latest_tx.timestamp,
                    120.0  # Max reasonable speed km/h
                )
                if is_violation:
                    reasons.append(reason)
                    score += rule_score
        
        # Determine Severity based on improved scoring thresholds
        severity = self._calculate_severity(score)
        
        # Log detection
        if score > 20:
            logger.warning(
                f"Anomaly detected: Transaction {transaction.transaction_id}",
                extra={
                    "vehicle_id": transaction.vehicle_id,
                    "risk_score": score,
                    "severity": severity,
                    "reasons": reasons
                }
            )
        
        return AnomalyResult(
            transaction_id=transaction.transaction_id,
            is_anomalous=score > 20,
            severity=severity,
            risk_score=min(score, 100),  # Cap at 100
            reasons=reasons
        )
    
    def _calculate_severity(self, score: int) -> str:
        """
        Calculate severity level from risk score.
        
        Args:
            score: Risk score
        
        Returns:
            Severity level string
        """
        if score >= 71:
            return "Critical"
        elif score >= 41:
            return "High"
        elif score >= 21:
            return "Medium"
        elif score > 0:
            return "Low"
        else:
            return "Low"  # Normal, no anomalies
