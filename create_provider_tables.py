"""
Create provider-related database tables.
Run this after adding provider integration.
"""
import asyncio
from backend.database import Base, async_engine

async def create_provider_tables():
    # Import models to register them
    from backend.db_models import ProviderCredentialDB, ProviderSyncLogDB
    
    async with async_engine.begin() as conn:
        # Create only the new provider tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("Provider tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_provider_tables())
