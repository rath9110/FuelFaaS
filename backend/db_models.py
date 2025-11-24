from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base


class VehicleStatus(str, enum.Enum):
    """Vehicle status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class SeverityLevel(str, enum.Enum):
    """Anomaly severity levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class FuelProvider(str, enum.Enum):
    """Fuel provider enumeration."""
    OKQ8 = "okq8"
    PREEM = "preem"
    SHELL = "shell"
    CIRCLEK = "circlek"


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


class UserDB(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    company_id = Column(String(100), index=True)  # For multi-tenancy
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))


class VehicleDB(Base):
    """Vehicle model."""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(String(100), nullable=False)
    tank_capacity_liters = Column(Float, nullable=False)
    reg_number = Column(String(50), unique=True, nullable=False)
    assigned_to_project = Column(String(50), ForeignKey("projects.project_id"), nullable=True)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.ACTIVE)
    company_id = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("ProjectDB", back_populates="vehicles")
    transactions = relationship("TransactionDB", back_populates="vehicle")


class ProjectDB(Base):
    """Project model with geofencing."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    geofence_lat = Column(Float, nullable=False)
    geofence_lon = Column(Float, nullable=False)
    geofence_radius_km = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    company_id = Column(String(100), index=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vehicles = relationship("VehicleDB", back_populates="project")
    workers = relationship("WorkerDB", secondary="worker_projects", back_populates="projects")


class WorkerDB(Base):
    """Worker/Driver model."""
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    schedule_start = Column(String(5), nullable=False)  # HH:MM format
    schedule_end = Column(String(5), nullable=False)    # HH:MM format
    company_id = Column(String(100), index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("ProjectDB", secondary="worker_projects", back_populates="workers")
    transactions = relationship("TransactionDB", back_populates="driver")


# Association table for many-to-many relationship
class WorkerProjectDB(Base):
    """Association table for workers and projects."""
    __tablename__ = "worker_projects"
    
    id = Column(Integer, primary_key=True)
    worker_id = Column(String(50), ForeignKey("workers.worker_id"), nullable=False)
    project_id = Column(String(50), ForeignKey("projects.project_id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())


class TransactionDB(Base):
    """Fuel transaction model."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    provider = Column(Enum(FuelProvider), nullable=False)
    card_id = Column(String(50), index=True, nullable=False)
    vehicle_id = Column(String(50), ForeignKey("vehicles.vehicle_id"), nullable=False)
    driver_id = Column(String(50), ForeignKey("workers.worker_id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    liters = Column(Float, nullable=False)
    price_per_liter = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fuel_type = Column(String(50), nullable=False)
    station_id = Column(String(100), nullable=False)
    station_lat = Column(Float, nullable=False)
    station_lon = Column(Float, nullable=False)
    company_id = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vehicle = relationship("VehicleDB", back_populates="transactions")
    driver = relationship("WorkerDB", back_populates="transactions")
    anomaly = relationship("AnomalyDB", back_populates="transaction", uselist=False)


class AnomalyDB(Base):
    """Detected anomaly/fraud model."""
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), ForeignKey("transactions.transaction_id"), unique=True, nullable=False)
    is_anomalous = Column(Boolean, default=True, nullable=False)
    severity = Column(Enum(SeverityLevel), nullable=False, index=True)
    risk_score = Column(Integer, nullable=False)
    reasons = Column(JSON, nullable=False)  # Store as JSON array
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, confirmed, false_positive, resolved
    company_id = Column(String(100), index=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transaction = relationship("TransactionDB", back_populates="anomaly")
    reviewer = relationship("UserDB")
