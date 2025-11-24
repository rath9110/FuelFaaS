"""
Pytest configuration and fixtures for FuelGuard AI tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from datetime import datetime

from backend.database import Base, get_db
from backend.main import app
from backend.config import settings
from backend.db_models import UserDB, VehicleDB, ProjectDB, WorkerDB, TransactionDB, AnomalyDB
from backend.auth import create_access_token, hash_password


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database dependency override."""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
async def test_user(test_db: AsyncSession) -> UserDB:
    """Create a test user."""
    user = UserDB(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("testpass123"),
        role="viewer",
        is_active=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_admin(test_db: AsyncSession) -> UserDB:
    """Create a test admin user."""
    admin = UserDB(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("adminpass123"),
        role="admin",
        is_active=True
    )
    test_db.add(admin)
    await test_db.commit()
    await test_db.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user: UserDB) -> str:
    """Generate JWT token for test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def admin_token(test_admin: UserDB) -> str:
    """Generate JWT token for test admin."""
    return create_access_token(data={"sub": str(test_admin.id)})


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Create authorization headers with user token."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Create authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================================
# Entity Fixtures
# ============================================================================

@pytest.fixture
async def test_vehicle(test_db: AsyncSession) -> VehicleDB:
    """Create a test vehicle."""
    vehicle = VehicleDB(
        vehicle_id="V001",
        type="Excavator",
        tank_capacity_liters=200.0,
        reg_number="ABC-123",
        assigned_to_project="P001",
        status="active"
    )
    test_db.add(vehicle)
    await test_db.commit()
    await test_db.refresh(vehicle)
    return vehicle


@pytest.fixture
async def test_project(test_db: AsyncSession) -> ProjectDB:
    """Create a test project."""
    project = ProjectDB(
        project_id="P001",
        name="Stockholm City Line",
        geofence_lat=59.3293,
        geofence_lon=18.0686,
        geofence_radius_km=5.0,
        active=True
    )
    test_db.add(project)
    await test_db.commit()
    await test_db.refresh(project)
    return project


@pytest.fixture
async def test_worker(test_db: AsyncSession) -> WorkerDB:
    """Create a test worker."""
    worker = WorkerDB(
        worker_id="W001",
        name="John Doe",
        schedule_start="07:00",
        schedule_end="16:00",
        is_active=True
    )
    test_db.add(worker)
    await test_db.commit()
    await test_db.refresh(worker)
    return worker


@pytest.fixture
async def test_transaction(test_db: AsyncSession, test_vehicle: VehicleDB) -> TransactionDB:
    """Create a test fuel transaction."""
    transaction = TransactionDB(
        transaction_id="TX001",
        provider="okq8",
        card_id="CARD123",
        vehicle_id=test_vehicle.vehicle_id,
        timestamp=datetime(2025, 11, 24, 14, 30, 0),
        liters=50.0,
        price_per_liter=20.5,
        total_amount=1025.0,
        fuel_type="Diesel",
        station_id="S001",
        station_lat=59.3293,
        station_lon=18.0686
    )
    test_db.add(transaction)
    await test_db.commit()
    await test_db.refresh(transaction)
    return transaction


@pytest.fixture
async def test_anomaly(test_db: AsyncSession, test_transaction: TransactionDB) -> AnomalyDB:
    """Create a test anomaly."""
    anomaly = AnomalyDB(
        transaction_id=test_transaction.transaction_id,
        is_anomalous=True,
        severity="High",
        risk_score=45,
        reasons=["Tank capacity exceeded", "Out of hours fueling"],
        reviewed=False,
        status="pending"
    )
    test_db.add(anomaly)
    await test_db.commit()
    await test_db.refresh(anomaly)
    return anomaly


# ============================================================================
# Factory Fixtures
# ============================================================================

@pytest.fixture
def vehicle_factory(test_db: AsyncSession):
    """Factory for creating test vehicles."""
    async def _create_vehicle(**kwargs):
        defaults = {
            "vehicle_id": f"V{datetime.now().timestamp()}",
            "type": "Truck",
            "tank_capacity_liters": 100.0,
            "reg_number": "TEST-999",
            "status": "active"
        }
        defaults.update(kwargs)
        vehicle = VehicleDB(**defaults)
        test_db.add(vehicle)
        await test_db.commit()
        await test_db.refresh(vehicle)
        return vehicle
    
    return _create_vehicle


@pytest.fixture
def transaction_factory(test_db: AsyncSession):
    """Factory for creating test transactions."""
    async def _create_transaction(**kwargs):
        defaults = {
            "transaction_id": f"TX{datetime.now().timestamp()}",
            "provider": "okq8",
            "card_id": "CARD001",
            "vehicle_id": "V001",
            "timestamp": datetime.now(),
            "liters": 50.0,
            "price_per_liter": 20.0,
            "total_amount": 1000.0,
            "fuel_type": "Diesel",
            "station_id": "S001",
            "station_lat": 59.0,
            "station_lon": 18.0
        }
        defaults.update(kwargs)
        transaction = TransactionDB(**defaults)
        test_db.add(transaction)
        await test_db.commit()
        await test_db.refresh(transaction)
        return transaction
    
    return _create_transaction
