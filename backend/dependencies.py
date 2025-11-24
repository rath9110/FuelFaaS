from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .logger import get_logger

logger = get_logger(__name__)


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Alias for get_db for clearer naming in routes.
    """
    async for session in get_db():
        yield session


# Pagination helper
class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(self, skip: int = 0, limit: int = 100):
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Skip parameter must be >= 0"
            )
        if limit <= 0 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Limit parameter must be between 1 and 1000"
            )
        self.skip = skip
        self.limit = limit


def get_pagination(skip: int = 0, limit: int = 100) -> PaginationParams:
    """Dependency for pagination parameters."""
    return PaginationParams(skip=skip, limit=limit)


# Company ID helper (for multi-tenancy)
# Will be enhanced in Phase 4 with actual user authentication
async def get_company_id(
    company_id: Optional[str] = None
) -> Optional[str]:
    """
    Get company ID for multi-tenancy.
    Currently accepts optional query parameter.
    Will be replaced with authenticated user's company in Phase 4.
    """
    return company_id
