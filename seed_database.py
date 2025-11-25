"""
Seed script to populate the database with sample data for demonstration.
Run this after initializing the database with Alembic.
"""

import asyncio
from datetime import datetime, timedelta
from backend.database import AsyncSessionLocal, init_db
from backend.db_models import (
    UserDB, VehicleDB, ProjectDB, WorkerDB, TransactionDB, AnomalyDB,
    WorkerProjectDB
)
from backend.auth import hash_password

async def seed_database():
    """Populate database with sample data."""
    
    print("🌱 Seeding database with sample data...")
    
    async with AsyncSessionLocal() as db:
        # Create admin user
        admin = UserDB(
            email="admin@fuelguard.ai",
            username="admin",
            full_name="Admin User",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        
        # Create projects
        projects = [
            ProjectDB(
                project_id="P001",
                name="Stockholm City Center Construction",
                geofence_lat=59.3293,
                geofence_lon=18.0686,
                geofence_radius_km=5.0,
                active=True
            ),
            ProjectDB(
                project_id="P002",
                name="Gothenburg Harbor Expansion",
                geofence_lat=57.7089,
                geofence_lon=11.9746,
                geofence_radius_km=10.0,
                active=True
            ),
        ]
        for project in projects:
            db.add(project)
        
        # Create workers
        workers = [
            WorkerDB(
                worker_id="W001",
                name="Erik Andersson",
                schedule_start="07:00",
                schedule_end="16:00",
                is_active=True
            ),
            WorkerDB(
                worker_id="W002",
                name="Anna Johansson",
                schedule_start="06:00",
                schedule_end="15:00",
                is_active=True
            ),
        ]
        for worker in workers:
            db.add(worker)
        
        # Create vehicles
        vehicles = [
            VehicleDB(
                vehicle_id="V001",
                type="Excavator",
                tank_capacity_liters=200.0,
                reg_number="ABC-123",
                assigned_to_project="P001",
                status="active"
            ),
            VehicleDB(
                vehicle_id="V002",
                type="Dump Truck",
                tank_capacity_liters=300.0,
                reg_number="XYZ-789",
                assigned_to_project="P001",
                status="active"
            ),
            VehicleDB(
                vehicle_id="V003",
                type="Crane",
                tank_capacity_liters=150.0,
                reg_number="DEF-456",
                assigned_to_project="P002",
                status="active"
            ),
        ]
        for vehicle in vehicles:
            db.add(vehicle)
        
        # Assign workers to projects
        worker_projects = [
            WorkerProjectDB(worker_id="W001", project_id="P001"),
            WorkerProjectDB(worker_id="W002", project_id="P002"),
        ]
        for wp in worker_projects:
            db.add(wp)
        
        await db.commit()
        print("✅ Created users, projects, workers, and vehicles")
        
        # Create sample transactions (mix of clean and suspicious)
        base_time = datetime.now() - timedelta(days=7)
        
        transactions = [
            # Clean transactions
            TransactionDB(
                transaction_id="TX001",
                provider="okq8",
                card_id="CARD001",
                vehicle_id="V001",
                driver_id="W001",
                timestamp=base_time + timedelta(hours=10),
                liters=50.0,
                price_per_liter=18.5,
                total_amount=925.0,
                fuel_type="Diesel",
                station_id="S001",
                station_lat=59.33,
                station_lon=18.07
            ),
            TransactionDB(
                transaction_id="TX002",
                provider="preem",
                card_id="CARD002",
                vehicle_id="V002",
                driver_id="W001",
                timestamp=base_time + timedelta(days=1, hours=11),
                liters=75.0,
                price_per_liter=18.2,
                total_amount=1365.0,
                fuel_type="Diesel",
                station_id="S002",
                station_lat=59.32,
                station_lon=18.08
            ),
            # Suspicious: Out of hours
            TransactionDB(
                transaction_id="TX003",
                provider="shell",
                card_id="CARD001",
                vehicle_id="V001",
                driver_id="W001",
                timestamp=base_time + timedelta(days=2, hours=22),  # 10 PM
                liters=45.0,
                price_per_liter=19.0,
                total_amount=855.0,
                fuel_type="Diesel",
                station_id="S003",
                station_lat=59.31,
                station_lon=18.06
            ),
            # Suspicious: Tank capacity exceeded
            TransactionDB(
                transaction_id="TX004",
                provider="circlek",
                card_id="CARD003",
                vehicle_id="V003",
                driver_id="W002",
                timestamp=base_time + timedelta(days=3, hours=13),
                liters=180.0,  # Exceeds 150L tank capacity
                price_per_liter=18.8,
                total_amount=3384.0,
                fuel_type="Diesel",
                station_id="S004",
                station_lat=57.71,
                station_lon=11.98
            ),
            # Suspicious: Weekend fueling
            TransactionDB(
                transaction_id="TX005",
                provider="okq8",
                card_id="CARD002",
                vehicle_id="V002",
                driver_id="W001",
                timestamp=base_time + timedelta(days=5, hours=14),  # Weekend
                liters=60.0,
                price_per_liter=20.5,  # Also high price
                total_amount=1230.0,
                fuel_type="Diesel",
                station_id="S001",
                station_lat=59.33,
                station_lon=18.07
            ),
            # Very suspicious: Multiple violations
            TransactionDB(
                transaction_id="TX006",
                provider="shell",
                card_id="CARD001",
                vehicle_id="V001",
                driver_id="W001",
                timestamp=base_time + timedelta(days=6, hours=3),  # 3 AM Sunday
                liters=250.0,  # Way over capacity
                price_per_liter=25.0,  # Very high price
                total_amount=6250.0,
                fuel_type="Diesel",
                station_id="S999",
                station_lat=60.5,  # Far from project
                station_lon=19.5
            ),
        ]
        
        for tx in transactions:
            db.add(tx)
        
        await db.commit()
        print("✅ Created sample transactions")
        
        # Create anomalies for suspicious transactions
        anomalies = [
            AnomalyDB(
                transaction_id="TX003",
                is_anomalous=True,
                severity="Medium",
                risk_score=25,
                reasons=["Out of hours fueling (outside 07:00-16:00)"],
                reviewed=False,
                status="pending"
            ),
            AnomalyDB(
                transaction_id="TX004",
                is_anomalous=True,
                severity="High",
                risk_score=40,
                reasons=["Fuel volume (180.0L) exceeds tank capacity (150.0L)"],
                reviewed=False,
                status="pending"
            ),
            AnomalyDB(
                transaction_id="TX005",
                is_anomalous=True,
                severity="Medium",
                risk_score=35,
                reasons=[
                    "Weekend fueling detected",
                    "Price 13.9% above market average"
                ],
                reviewed=False,
                status="pending"
            ),
            AnomalyDB(
                transaction_id="TX006",
                is_anomalous=True,
                severity="Critical",
                risk_score=95,
                reasons=[
                    "Out of hours fueling (outside 07:00-16:00)",
                    "Weekend fueling detected",
                    "Fuel volume (250.0L) exceeds tank capacity (200.0L)",
                    "Price 38.9% above market average",
                    "Station 131.2 km away from project P001"
                ],
                reviewed=False,
                status="pending"
            ),
        ]
        
        for anomaly in anomalies:
            db.add(anomaly)
        
        await db.commit()
        print("✅ Created anomaly records")
        
    print("\n🎉 Database seeding complete!")
    print("\n📝 Sample credentials:")
    print("   Username: admin")
    print("   Password: admin123")

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(seed_database())
