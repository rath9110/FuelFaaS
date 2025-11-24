from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_pagination, PaginationParams, get_company_id
from ..models import Project, ProjectCreate, ProjectUpdate
from ..db_models import ProjectDB
from ..exceptions import NotFoundException
from ..logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project, status_code=201)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Create a new project."""
    db_project = ProjectDB(**project.model_dump(), company_id=company_id)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    logger.info(f"Project created: {project.project_id}")
    return Project.model_validate(db_project)


@router.get("/", response_model=List[Project])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    company_id: Optional[str] = Depends(get_company_id),
    active: Optional[bool] = None
):
    """List all projects with optional filtering."""
    query = select(ProjectDB)
    
    filters = []
    if company_id:
        filters.append(ProjectDB.company_id == company_id)
    if active is not None:
        filters.append(ProjectDB.active == active)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(pagination.skip).limit(pagination.limit)
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return [Project.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Get a specific project by ID."""
    query = select(ProjectDB).where(ProjectDB.project_id == project_id)
    
    if company_id:
        query = query.where(ProjectDB.company_id == company_id)
    
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundException("Project", project_id)
    
    return Project.model_validate(project)


@router.patch("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Update a project."""
    query = select(ProjectDB).where(ProjectDB.project_id == project_id)
    
    if company_id:
        query = query.where(ProjectDB.company_id == company_id)
    
    result = await db.execute(query)
    db_project = result.scalar_one_or_none()
    
    if not db_project:
        raise NotFoundException("Project", project_id)
    
    # Update fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    await db.commit()
    await db.refresh(db_project)
    
    logger.info(f"Project updated: {project_id}")
    return Project.model_validate(db_project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    company_id: Optional[str] = Depends(get_company_id)
):
    """Delete a project."""
    query = select(ProjectDB).where(ProjectDB.project_id == project_id)
    
    if company_id:
        query = query.where(ProjectDB.company_id == company_id)
    
    result = await db.execute(query)
    db_project = result.scalar_one_or_none()
    
    if not db_project:
        raise NotFoundException("Project", project_id)
    
    await db.delete(db_project)
    await db.commit()
    
    logger.info(f"Project deleted: {project_id}")
