"""Provider management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User
from ..auth import get_current_user
from ..db_models import ProviderCredentialDB, ProviderSyncLogDB
from ..services.provider_sync import ProviderSyncService
from ..providers import PROVIDERS
from pydantic import BaseModel

router = APIRouter(prefix="/providers", tags=["providers"])


# Pydantic models
class ProviderCredentialCreate(BaseModel):
    provider_name: str
    credentials: dict


class ProviderCredentialResponse(BaseModel):
    id: int
    provider_name: str
    is_active: bool
    last_validated: Optional[datetime]
    created_at: datetime
   
    class Config:
        from_attributes = True


class SyncTrigger(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SyncLogResponse(BaseModel):
    id: int
    provider_name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    transactions_fetched: int
    transactions_created: int
    transactions_skipped: int
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/available")
async def list_available_providers():
    """List all available providers that can be configured."""
    return {
        "providers": list(PROVIDERS.keys()),
        "count": len(PROVIDERS)
    }


@router.post("/credentials", response_model=ProviderCredentialResponse)
async def add_provider_credential(
    credential_data: ProviderCredentialCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add new provider credentials.
    Validates credentials before saving.
    """
    if credential_data.provider_name.lower() not in PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider: {credential_data.provider_name}"
        )
    
    sync_service = ProviderSyncService(db)
    
    try:
        credential = await sync_service.add_provider_credential(
            provider_name=credential_data.provider_name,
            credentials=credential_data.credentials,
            created_by=current_user.id
        )
        return credential
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add provider: {str(e)}"
        )


@router.get("/credentials", response_model=List[ProviderCredentialResponse])
async def list_provider_credentials(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all configured provider credentials."""
    result = await db.execute(select(ProviderCredentialDB))
    credentials = result.scalars().all()
    return credentials


@router.delete("/credentials/{credential_id}")
async def delete_provider_credential(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete provider credentials."""
    result = await db.execute(
        select(ProviderCredentialDB).where(ProviderCredentialDB.id == credential_id)
    )
    credential = result.scalar_one_or_none()
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )
    
    await db.delete(credential)
    await db.commit()
    
    return {"message": "Credential deleted successfully"}


@router.post("/{provider_name}/sync", response_model=SyncLogResponse)
async def trigger_provider_sync(
    provider_name: str,
    sync_trigger: SyncTrigger,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger sync for a specific provider."""
    # Find active credential for this provider
    result = await db.execute(
        select(ProviderCredentialDB).where(
            ProviderCredentialDB.provider_name == provider_name.lower(),
            ProviderCredentialDB.is_active == True
        )
    )
    credential = result.scalar_one_or_none()
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active credentials found for provider: {provider_name}"
        )
    
    sync_service = ProviderSyncService(db)
    
    try:
        sync_log = await sync_service.sync_provider(
            credential_id=credential.id,
            start_date=sync_trigger.start_date,
            end_date=sync_trigger.end_date
        )
        return sync_log
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.post("/sync-all", response_model=List[SyncLogResponse])
async def trigger_all_providers_sync(
    sync_trigger: SyncTrigger,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger sync for all active providers."""
    sync_service = ProviderSyncService(db)
    
    try:
        sync_logs = await sync_service.sync_all_providers(
            start_date=sync_trigger.start_date,
            end_date=sync_trigger.end_date
        )
        return sync_logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/sync-logs", response_model=List[SyncLogResponse])
async def list_sync_logs(
    provider_name: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List sync history logs."""
    query = select(ProviderSyncLogDB).order_by(ProviderSyncLogDB.started_at.desc()).limit(limit)
    
    if provider_name:
        query = query.where(ProviderSyncLogDB.provider_name == provider_name.lower())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs


@router.get("/{provider_name}/status")
async def get_provider_status(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get status of a specific provider."""
    # Get credential
    cred_result = await db.execute(
        select(ProviderCredentialDB).where(
            ProviderCredentialDB.provider_name == provider_name.lower()
        )
    )
    credential = cred_result.scalar_one_or_none()
    
    if not credential:
        return {
            "provider_name": provider_name,
            "configured": False,
            "active": False
        }
    
    # Get latest sync log
    log_result = await db.execute(
        select(ProviderSyncLogDB)
        .where(ProviderSyncLogDB.credential_id == credential.id)
        .order_by(ProviderSyncLogDB.started_at.desc())
        .limit(1)
    )
    latest_log = log_result.scalar_one_or_none()
    
    return {
        "provider_name": provider_name,
        "configured": True,
        "active": credential.is_active,
        "last_validated": credential.last_validated,
        "last_sync": latest_log.started_at if latest_log else None,
        "last_sync_status": latest_log.status if latest_log else None,
        "last_sync_transactions": latest_log.transactions_created if latest_log else 0
    }
