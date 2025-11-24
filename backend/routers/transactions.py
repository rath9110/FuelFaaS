from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..dependencies import get_pagination, PaginationParams, get_company_id
from ..models import (
    FuelTransaction,
    FuelTransactionCreate,
    AnomalyResult,
    StatsResponse
)
from ..db_models import TransactionDB, AnomalyDB, VehicleDB
from ..engine import AnomalyEngine
from ..logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=AnomalyResult, status_code=201)
async def create_transaction(
    transaction: FuelTransactionCreate,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """
    Ingest a new fuel transaction and analyze for fraud.
    
    This endpoint:
    1. Creates a new transaction record
    2. Runs anomaly detection
    3. Stores any detected anomalies
    4. Returns the anomaly result
    """
    # Create transaction in database
    db_transaction = TransactionDB(
        **transaction.model_dump(),
        company_id=company_id
    )
    db.add(db_transaction)
    await db.flush()
    
    # Load vehicle, project, worker data for analysis
    vehicles_query = select(VehicleDB)
    vehicles_result = await db.execute(vehicles_query)
    vehicles_dict = {v.vehicle_id: v for v in vehicles_result.scalars().all()}
    
    # For now, using empty dicts for projects and workers
    # Will be populated when those endpoints are created
    projects_dict = {}
    workers_dict = {}
    
    # Run anomaly detection
    engine = AnomalyEngine(vehicles_dict, projects_dict, workers_dict, db)
    result = await engine.check_transaction(FuelTransaction.model_validate(db_transaction))
    
    # Store anomaly if detected
    if result.is_anomalous:
        db_anomaly = AnomalyDB(
            transaction_id=result.transaction_id,
            is_anomalous=result.is_anomalous,
            severity=result.severity,
            risk_score=result.risk_score,
            reasons=result.reasons,
            company_id=company_id
        )
        db.add(db_anomaly)
    
    await db.commit()
    
    logger.info(
        f"Transaction ingested: {transaction.transaction_id}",
        extra={"risk_score": result.risk_score, "is_anomalous": result.is_anomalous}
    )
    
    return result


@router.get("/", response_model=List[FuelTransaction])
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    company_id: Optional[str] = Depends(get_company_id),
    vehicle_id: Optional[str] = None,
    driver_id: Optional[str] = None,
    provider: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    List all fuel transactions with optional filtering.
    
    Filters:
    - vehicle_id: Filter by vehicle
    - driver_id: Filter by driver
    - provider: Filter by fuel provider
    - start_date: Transactions after this date
    - end_date: Transactions before this date
    """
    query = select(TransactionDB)
    
    # Build filters
    filters = []
    if company_id:
        filters.append(TransactionDB.company_id == company_id)
    if vehicle_id:
        filters.append(TransactionDB.vehicle_id == vehicle_id)
    if driver_id:
        filters.append(TransactionDB.driver_id == driver_id)
    if provider:
        filters.append(TransactionDB.provider == provider)
    if start_date:
        filters.append(TransactionDB.timestamp >= start_date)
    if end_date:
        filters.append(TransactionDB.timestamp <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(pagination.skip).limit(pagination.limit).order_by(TransactionDB.timestamp.desc())
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return [FuelTransaction.model_validate(tx) for tx in transactions]


@router.get("/{transaction_id}", response_model=FuelTransaction)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Get a specific transaction by ID."""
    query = select(TransactionDB).where(TransactionDB.transaction_id == transaction_id)
    
    if company_id:
        query = query.where(TransactionDB.company_id == company_id)
    
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
    
    return FuelTransaction.model_validate(transaction)
