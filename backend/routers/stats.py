from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional

from ..database import get_db
from ..dependencies import get_company_id
from ..models import StatsResponse
from ..db_models import TransactionDB, AnomalyDB, SeverityLevel
from ..logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/", response_model=StatsResponse)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """
    Get overall statistics and metrics.
    
    Returns:
    - Total number of transactions
    - Total number of anomalies
    - Average risk score
    - Breakdown by severity level
    """
    # Total transactions
    tx_query = select(func.count(TransactionDB.id))
    if company_id:
        tx_query = tx_query.where(TransactionDB.company_id == company_id)
    tx_result = await db.execute(tx_query)
    total_transactions = tx_result.scalar() or 0
    
    # Total anomalies
    anomaly_base_query = select(AnomalyDB)
    if company_id:
        anomaly_base_query = anomaly_base_query.where(AnomalyDB.company_id == company_id)
    
    anomaly_count_query = select(func.count(AnomalyDB.id)).select_from(anomaly_base_query.subquery())
    anomaly_result = await db.execute(anomaly_count_query)
    total_anomalies = anomaly_result.scalar() or 0
    
    # Average risk score
    avg_score_query = select(func.avg(AnomalyDB.risk_score))
    if company_id:
        avg_score_query = avg_score_query.where(AnomalyDB.company_id == company_id)
    avg_result = await db.execute(avg_score_query)
    average_risk_score = float(avg_result.scalar() or 0)
    
    # Breakdown by severity
    severity_counts = {
        "critical_anomalies": 0,
        "high_anomalies": 0,
        "medium_anomalies": 0,
        "low_anomalies": 0
    }
    
    for severity_level, key in [
        (SeverityLevel.CRITICAL, "critical_anomalies"),
        (SeverityLevel.HIGH, "high_anomalies"),
        (SeverityLevel.MEDIUM, "medium_anomalies"),
        (SeverityLevel.LOW, "low_anomalies")
    ]:
        severity_query = select(func.count(AnomalyDB.id)).where(
            AnomalyDB.severity == severity_level
        )
        if company_id:
            severity_query = severity_query.where(AnomalyDB.company_id == company_id)
        
        result = await db.execute(severity_query)
        severity_counts[key] = result.scalar() or 0
    
    return StatsResponse(
        total_transactions=total_transactions,
        total_anomalies=total_anomalies,
        average_risk_score=average_risk_score,
        **severity_counts
    )
