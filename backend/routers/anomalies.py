from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..dependencies import get_pagination, PaginationParams, get_company_id
from ..models import AnomalyResult, AnomalyUpdate
from ..db_models import AnomalyDB, TransactionDB
from ..exceptions import NotFoundException
from ..logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("/", response_model=List[AnomalyResult])
async def list_anomalies(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    company_id: Optional[str] = Depends(get_company_id),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    reviewed: Optional[bool] = None
):
    """
    List all detected anomalies with optional filtering.
    
    Filters:
    - severity: Filter by severity level (Low, Medium, High, Critical)
    - status: Filter by status (pending, confirmed, false_positive, resolved)
    - start_date/end_date: Filter by detection date range
    - reviewed: Filter by review status
    """
    query = select(AnomalyDB)
    
    filters = []
    if company_id:
        filters.append(AnomalyDB.company_id == company_id)
    if severity:
        filters.append(AnomalyDB.severity == severity)
    if status:
        filters.append(AnomalyDB.status == status)
    if reviewed is not None:
        filters.append(AnomalyDB.reviewed == reviewed)
    if start_date:
        filters.append(AnomalyDB.detected_at >= start_date)
    if end_date:
        filters.append(AnomalyDB.detected_at <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(pagination.skip).limit(pagination.limit).order_by(AnomalyDB.detected_at.desc())
    
    result = await db.execute(query)
    anomalies = result.scalars().all()
    
    return [AnomalyResult.model_validate(a) for a in anomalies]


@router.get("/{anomaly_id}", response_model=AnomalyResult)
async def get_anomaly(
    anomaly_id: int,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Get a specific anomaly by ID."""
    query = select(AnomalyDB).where(AnomalyDB.id == anomaly_id)
    
    if company_id:
        query = query.where(AnomalyDB.company_id == company_id)
    
    result = await db.execute(query)
    anomaly = result.scalar_one_or_none()
    
    if not anomaly:
        raise NotFoundException("Anomaly", str(anomaly_id))
    
    return AnomalyResult.model_validate(anomaly)


@router.patch("/{anomaly_id}", response_model=AnomalyResult)
async def review_anomaly(
    anomaly_id: int,
    anomaly_update: AnomalyUpdate,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """
    Review and update an anomaly.
    Used for marking anomalies as confirmed, false positive, or resolved.
    """
    query = select(AnomalyDB).where(AnomalyDB.id == anomaly_id)
    
    if company_id:
        query = query.where(AnomalyDB.company_id == company_id)
    
    result = await db.execute(query)
    db_anomaly = result.scalar_one_or_none()
    
    if not db_anomaly:
        raise NotFoundException("Anomaly", str(anomaly_id))
    
    # Update fields
    update_data = anomaly_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_anomaly, field, value)
    
    # Set reviewed timestamp
    if anomaly_update.reviewed:
        db_anomaly.reviewed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_anomaly)
    
    logger.info(f"Anomaly reviewed: {anomaly_id}, status: {db_anomaly.status}")
    return AnomalyResult.model_validate(db_anomaly)
