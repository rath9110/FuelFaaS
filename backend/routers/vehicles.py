from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_pagination, PaginationParams, get_company_id
from .. models import Vehicle, VehicleCreate, VehicleUpdate
from ..db_models import VehicleDB
from ..exceptions import NotFoundException
from ..logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("/", response_model=Vehicle, status_code=201)
async def create_vehicle(
    vehicle: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Create a new vehicle."""
    db_vehicle = VehicleDB(**vehicle.model_dump(), company_id=company_id)
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    
    logger.info(f"Vehicle created: {vehicle.vehicle_id}")
    return Vehicle.model_validate(db_vehicle)


@router.get("/", response_model=List[Vehicle])
async def list_vehicles(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    company_id: Optional[str] = Depends(get_company_id),
    status: Optional[str] = None,
    assigned_to_project: Optional[str] = None
):
    """List all vehicles with optional filtering."""
    query = select(VehicleDB)
    
    filters = []
    if company_id:
        filters.append(VehicleDB.company_id == company_id)
    if status:
        filters.append(VehicleDB.status == status)
    if assigned_to_project:
        filters.append(VehicleDB.assigned_to_project == assigned_to_project)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(pagination.skip).limit(pagination.limit)
    
    result = await db.execute(query)
    vehicles = result.scalars().all()
    
    return [Vehicle.model_validate(v) for v in vehicles]


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(
    vehicle_id: str,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Get a specific vehicle by ID."""
    query = select(VehicleDB).where(VehicleDB.vehicle_id == vehicle_id)
    
    if company_id:
        query = query.where(VehicleDB.company_id == company_id)
    
    result = await db.execute(query)
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise NotFoundException("Vehicle", vehicle_id)
    
    return Vehicle.model_validate(vehicle)


@router.patch("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Update a vehicle."""
    query = select(VehicleDB).where(VehicleDB.vehicle_id == vehicle_id)
    
    if company_id:
        query = query.where(VehicleDB.company_id == company_id)
    
    result = await db.execute(query)
    db_vehicle = result.scalar_one_or_none()
    
    if not db_vehicle:
        raise NotFoundException("Vehicle", vehicle_id)
    
    # Update fields
    update_data = vehicle_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    
    await db.commit()
    await db.refresh(db_vehicle)
    
    logger.info(f"Vehicle updated: {vehicle_id}")
    return Vehicle.model_validate(db_vehicle)


@router.delete("/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: str,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Delete a vehicle."""
    query = select(VehicleDB).where(VehicleDB.vehicle_id == vehicle_id)
    
    if company_id:
        query = query.where(VehicleDB.company_id == company_id)
    
    result = await db.execute(query)
    db_vehicle = result.scalar_one_or_none()
    
    if not db_vehicle:
        raise NotFoundException("Vehicle", vehicle_id)
    
    await db.delete(db_vehicle)
    await db.commit()
    
    logger.info(f"Vehicle deleted: {vehicle_id}")
