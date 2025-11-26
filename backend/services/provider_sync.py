"""Provider sync service for automatic transaction importing."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from cryptography.fernet import Fernet
import json

from ..providers import get_provider, ProviderError
from ..db_models import (
    ProviderCredentialDB,
    ProviderSyncLogDB,
    TransactionDB,
)
from ..models import FuelTransaction
from ..engine import AnomalyEngine
from ..logger import get_logger

logger = get_logger(__name__)


class ProviderSyncService:
    """Service for syncing transactions from fuel card providers."""
    
    def __init__(self, db: AsyncSession, encryption_key: Optional[bytes] = None):
        """
        Initialize sync service.
        
        Args:
            db: Database session
            encryption_key: Key for encrypting/decrypting credentials
        """
        self.db = db
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_credentials(self, credentials: dict) -> str:
        """Encrypt credentials dictionary to string."""
        json_data = json.dumps(credentials)
        encrypted = self.cipher.encrypt(json_data.encode())
        return encrypted.decode()
    
    def decrypt_credentials(self, encrypted: str) -> dict:
        """Decrypt credentials string to dictionary."""
        decrypted = self.cipher.decrypt(encrypted.encode())
        return json.loads(decrypted.decode())
    
    async def add_provider_credential(
        self,
        provider_name: str,
        credentials: dict,
        created_by: Optional[int] = None
    ) -> ProviderCredentialDB:
        """
        Add new provider credentials.
        
        Args:
            provider_name: Provider identifier (okq8, preem, shell, circlek)
            credentials: Provider-specific credentials
            created_by: User ID who added the credentials
            
        Returns:
            Created credential record
        """
        # Validate credentials by testing connection
        provider = get_provider(provider_name, credentials)
        await provider.validate_credentials()
        
        # Encrypt and save
        encrypted = self.encrypt_credentials(credentials)
        credential = ProviderCredentialDB(
            provider_name=provider_name.lower(),
            credentials_encrypted=encrypted,
            is_active=True,
            last_validated=datetime.utcnow(),
            created_by=created_by
        )
        
        self.db.add(credential)
        await self.db.commit()
        await self.db.refresh(credential)
        
        logger.info(f"Added credentials for provider: {provider_name}")
        return credential
    
    async def sync_provider(
        self,
        credential_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ProviderSyncLogDB:
        """
        Sync transactions from a provider.
        
        Args:
            credential_id: Provider credential ID
            start_date: Start of sync range (defaults to 7 days ago)
            end_date: End of sync range (defaults to now)
            
        Returns:
            Sync log record
        """
        # Get credentials
        result = await self.db.execute(
            select(ProviderCredentialDB).where(ProviderCredentialDB.id == credential_id)
        )
        credential = result.scalar_one_or_none()
        
        if not credential:
            raise ValueError(f"Credential {credential_id} not found")
        
        if not credential.is_active:
            raise ValueError(f"Credential {credential_id} is inactive")
        
        # Default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # Create sync log
        sync_log = ProviderSyncLogDB(
            credential_id=credential_id,
            provider_name=credential.provider_name,
            status="started",
            sync_range_start=start_date,
            sync_range_end=end_date
        )
        self.db.add(sync_log)
        await self.db.commit()
        await self.db.refresh(sync_log)
        
        logger.info(
            f"Starting sync for {credential.provider_name} "
            f"from {start_date} to {end_date}"
        )
        
        try:
            # Decrypt credentials and get provider client
            creds = self.decrypt_credentials(credential.credentials_encrypted)
            provider = get_provider(credential.provider_name, creds)
            
            # Fetch transactions
            transactions = await provider.get_transactions(start_date, end_date)
            sync_log.transactions_fetched = len(transactions)
            
            logger.info(f"Fetched {len(transactions)} transactions from {credential.provider_name}")
            
            # Process each transaction
            created_count = 0
            skipped_count = 0
            
            for tx in transactions:
                # Check for duplicates
                existing = await self.db.execute(
                    select(TransactionDB).where(
                        TransactionDB.transaction_id == tx.transaction_id
                    )
                )
                if existing.scalar_one_or_none():
                    skipped_count += 1
                    logger.debug(f"Skipping duplicate transaction: {tx.transaction_id}")
                    continue
                
                # Create transaction
                tx_db = TransactionDB(
                    transaction_id=tx.transaction_id,
                    provider=tx.provider,
                    card_id=tx.card_id,
                    vehicle_id=tx.vehicle_id,
                    driver_id=tx.driver_id,
                    timestamp=tx.timestamp,
                    liters=tx.liters,
                    price_per_liter=tx.price_per_liter,
                    total_amount=tx.total_amount,
                    fuel_type=tx.fuel_type,
                    station_id=tx.station_id,
                    station_lat=tx.station_lat,
                    station_lon=tx.station_lon,
                    provider_sync_id=sync_log.id
                )
                self.db.add(tx_db)
                created_count += 1
                
                # Run fraud detection
                try:
                    engine = AnomalyEngine(self.db)
                    await engine.analyze_and_save(tx)
                    logger.debug(f"Fraud detection completed for: {tx.transaction_id}")
                except Exception as e:
                    logger.error(f"Fraud detection failed for {tx.transaction_id}: {e}")
            
            await self.db.commit()
            
            # Update sync log
            sync_log.status = "success"
            sync_log.completed_at = datetime.utcnow()
            sync_log.transactions_created = created_count
            sync_log.transactions_skipped = skipped_count
            await self.db.commit()
            
            logger.info(
                f"Sync completed for {credential.provider_name}: "
                f"{created_count} created, {skipped_count} skipped"
            )
            
        except Exception as e:
            # Log error
            sync_log.status = "failed"
            sync_log.completed_at = datetime.utcnow()
            sync_log.error_message = str(e)
            await self.db.commit()
            
            logger.error(f"Sync failed for {credential.provider_name}: {e}")
            raise
        
        return sync_log
    
    async def sync_all_providers(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ProviderSyncLogDB]:
        """
        Sync all active provider credentials.
        
        Args:
            start_date: Start of sync range
            end_date: End of sync range
            
        Returns:
            List of sync log records
        """
        # Get all active credentials
        result = await self.db.execute(
            select(ProviderCredentialDB).where(ProviderCredentialDB.is_active == True)
        )
        credentials = result.scalars().all()
        
        logger.info(f"Starting sync for {len(credentials)} providers")
        
        sync_logs = []
        for cred in credentials:
            try:
                sync_log = await self.sync_provider(cred.id, start_date, end_date)
                sync_logs.append(sync_log)
            except Exception as e:
                logger.error(f"Failed to sync provider {cred.provider_name}: {e}")
                continue
        
        logger.info(f"Completed sync for {len(sync_logs)} providers")
        return sync_logs
