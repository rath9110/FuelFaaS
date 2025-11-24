from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_pagination, PaginationParams, get_company_id
from ..models import Worker, WorkerCreate, WorkerUpdate
from ..db_models import WorkerDB, WorkerProjectDB
from ..exceptions import NotFoundException
from ..logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("/", response_model=Worker, status_code=201)
async def create_worker(
    worker: WorkerCreate,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Create a new worker/driver."""
    db_worker = WorkerDB(
        worker_id=worker.worker_id,
        name=worker.name,
        schedule_start=worker.schedule_start,
        schedule_end=worker.schedule_end,
        company_id=company_id
    )
    db.add(db_worker)
    await db.flush()
    
    # Add project assignments
    for project_id in worker.assigned_project_ids:
        assignment = WorkerProjectDB(worker_id=worker.worker_id, project_id=project_id)
        db.add(assignment)
    
    await db.commit()
    await db.refresh(db_worker)
    
    logger.info(f"Worker created: {worker.worker_id}")
    
    # Build response with assigned projects
    result = Worker.model_validate(db_worker)
    result.assigned_project_ids = worker.assigned_project_ids
    return result


@router.get("/", response_model=List[Worker])
async def list_workers(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    company_id: Optional[str] = Depends(get_company_id),
    is_active: Optional[bool] = None
):
    """List all workers with optional filtering."""
    query = select(WorkerDB)
    
    filters = []
    if company_id:
        filters.append(WorkerDB.company_id == company_id)
    if is_active is not None:
        filters.append(WorkerDB.is_active == is_active)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(pagination.skip).limit(pagination.limit)
    
    result = await db.execute(query)
    workers = result.scalars().all()
    
    # Get project assignments for each worker
    workers_with_projects = []
    for worker in workers:
        assignments_query = select(WorkerProjectDB.project_id).where(
            WorkerProjectDB.worker_id == worker.worker_id
        )
        assignments_result = await db.execute(assignments_query)
        project_ids = [row[0] for row in assignments_result.all()]
        
        worker_model = Worker.model_validate(worker)
        worker_model.assigned_project_ids = project_ids
        workers_with_projects.append(worker_model)
    
    return workers_with_projects


@router.get("/{worker_id}", response_model=Worker)
async def get_worker(
    worker_id: str,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Get a specific worker by ID."""
    query = select(WorkerDB).where(WorkerDB.worker_id == worker_id)
    
    if company_id:
        query = query.where(WorkerDB.company_id == company_id)
    
    result = await db.execute(query)
    worker = result.scalar_one_or_none()
    
    if not worker:
        raise NotFoundException("Worker", worker_id)
    
    # Get project assignments
    assignments_query = select(WorkerProjectDB.project_id).where(
        WorkerProjectDB.worker_id == worker_id
    )
    assignments_result = await db.execute(assignments_query)
    project_ids = [row[0] for row in assignments_result.all()]
    
    worker_model = Worker.model_validate(worker)
    worker_model.assigned_project_ids = project_ids
    return worker_model


@router.patch("/{worker_id}", response_model=Worker)
async def update_worker(
    worker_id: str,
    worker_update: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Update a worker."""
    query = select(WorkerDB).where(WorkerDB.worker_id == worker_id)
    
    if company_id:
        query = query.where(WorkerDB.company_id == company_id)
    
    result = await db.execute(query)
    db_worker = result.scalar_one_or_none()
    
    if not db_worker:
        raise NotFoundException("Worker", worker_id)
    
    # Update fields
    update_data = worker_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_worker, field, value)
    
    await db.commit()
    await db.refresh(db_worker)
    
    logger.info(f"Worker updated: {worker_id}")
    
    # Get project assignments
    assignments_query = select(WorkerProjectDB.project_id).where(
        WorkerProjectDB.worker_id == worker_id
    )
    assignments_result = await db.execute(assignments_query)
    project_ids = [row[0] for row in assignments_result.all()]
    
    worker_model = Worker.model_validate(db_worker)
    worker_model.assigned_project_ids = project_ids
    return worker_model


@router.delete("/{worker_id}", status_code=204)
async def delete_worker(
    worker_id: str,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Delete a worker."""
    query = select(WorkerDB).where(WorkerDB.worker_id == worker_id)
    
    if company_id:
        query = query.where(WorkerDB.company_id == company_id)
    
    result = await db.execute(query)
    db_worker = result.scalar_one_or_none()
    
    if not db_worker:
        raise NotFoundException("Worker", worker_id)
    
    # Delete project assignments first
    delete_assignments = select(WorkerProjectDB).where(WorkerProjectDB.worker_id == worker_id)
    assignments_result = await db.execute(delete_assignments)
    for assignment in assignments_result.scalars().all():
        await db.delete(assignment)
    
    await db.delete(db_worker)
    await db.commit()
    
    logger.info(f"Worker deleted: {worker_id}")
