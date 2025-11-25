"""
Simple script to initialize database with tables.
"""
import asyncio
from backend.database import Base, async_engine

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
