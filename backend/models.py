from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime


# ============================================================================
# Base Schemas (for inheritance)
# ============================================================================

class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================================
# Transaction Schemas
# ============================================================================

class FuelTransactionBase(BaseModel):
    """Base fuel transaction model."""
    transaction_id: str
    provider: Literal['okq8', 'preem', 'shell', 'circlek']
    card_id: str
    vehicle_id: str
    driver_id: Optional[str] = None
    timestamp: datetime
    liters: float = Field(gt=0, description="Fuel amount in liters")
    price_per_liter: float = Field(gt=0, description="Price per liter")
    total_amount: float = Field(gt=0, description="Total transaction amount")
    fuel_type: str
    station_id: str
    station_lat: float = Field(ge=-90, le=90, description="Station latitude")
    station_lon: float = Field(ge=-180, le=180, description="Station longitude")


class FuelTransactionCreate(FuelTransactionBase):
    """Schema for creating a fuel transaction."""
    pass


class FuelTransaction(FuelTransactionBase, TimestampMixin):
    """Schema for fuel transaction response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    company_id: Optional[str] = None


# ============================================================================
# Vehicle Schemas
# ============================================================================

class VehicleBase(BaseModel):
    """Base vehicle model."""
    vehicle_id: str
    type: str
    tank_capacity_liters: float = Field(gt=0, description="Tank capacity in liters")
    reg_number: str
    assigned_to_project: Optional[str] = None
    status: Literal['active', 'inactive'] = 'active'


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle."""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle."""
    type: Optional[str] = None
    tank_capacity_liters: Optional[float] = Field(None, gt=0)
    reg_number: Optional[str] = None
    assigned_to_project: Optional[str] = None
    status: Optional[Literal['active', 'inactive']] = None


class Vehicle(VehicleBase, TimestampMixin):
    """Schema for vehicle response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    company_id: Optional[str] = None


# ============================================================================
# Project Schemas
# ============================================================================

class ProjectBase(BaseModel):
    """Base project model."""
    project_id: str
    name: str
    geofence_lat: float = Field(ge=-90, le=90, description="Geofence center latitude")
    geofence_lon: float = Field(ge=-180, le=180, description="Geofence center longitude")
    geofence_radius_km: float = Field(gt=0, description="Geofence radius in kilometers")
    active: bool = True


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = None
    geofence_lat: Optional[float] = Field(None, ge=-90, le=90)
    geofence_lon: Optional[float] = Field(None, ge=-180, le=180)
    geofence_radius_km: Optional[float] = Field(None, gt=0)
    active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Project(ProjectBase, TimestampMixin):
    """Schema for project response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    company_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ============================================================================
# Worker Schemas
# ============================================================================

class WorkerBase(BaseModel):
    """Base worker model."""
    worker_id: str
    name: str
    schedule_start: str = Field(pattern=r"^([01]\d|2[0-3]):([0-5]\d)$", description="HH:MM format")
    schedule_end: str = Field(pattern=r"^([01]\d|2[0-3]):([0-5]\d)$", description="HH:MM format")


class WorkerCreate(WorkerBase):
    """Schema for creating a worker."""
    assigned_project_ids: List[str] = []


class WorkerUpdate(BaseModel):
    """Schema for updating a worker."""
    name: Optional[str] = None
    schedule_start: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    schedule_end: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    is_active: Optional[bool] = None


class Worker(WorkerBase, TimestampMixin):
    """Schema for worker response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    assigned_project_ids: List[str] = []
    company_id: Optional[str] = None
    is_active: bool = True


# ============================================================================
# Anomaly Schemas
# ============================================================================

class AnomalyBase(BaseModel):
    """Base anomaly model."""
    transaction_id: str
    is_anomalous: bool
    severity: Literal['Low', 'Medium', 'High', 'Critical']
    risk_score: int = Field(ge=0, le=100, description="Risk score 0-100")
    reasons: List[str]


class AnomalyCreate(AnomalyBase):
    """Schema for creating an anomaly."""
    pass


class AnomalyUpdate(BaseModel):
    """Schema for updating an anomaly (review)."""
    reviewed: bool = True
    review_notes: Optional[str] = None
    status: Literal['pending', 'confirmed', 'false_positive', 'resolved'] = 'pending'


class AnomalyResult(AnomalyBase):
    """Schema for anomaly detection result."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    reviewed: bool = False
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    status: str = "pending"
    detected_at: Optional[datetime] = None


# ============================================================================
# User Schemas (Phase 4)
# ============================================================================

class UserBase(BaseModel):
    """Base user model."""
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(min_length=8)
    role: Literal['admin', 'manager', 'viewer'] = 'viewer'


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    full_name: Optional[str] = None
    role: Optional[Literal['admin', 'manager', 'viewer']] = None
    is_active: Optional[bool] = None


class User(UserBase, TimestampMixin):
    """Schema for user response (without password)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: Literal['admin', 'manager', 'viewer']
    is_active: bool
    last_login: Optional[datetime] = None


# ============================================================================
# Utility Schemas
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List[BaseModel]
    total: int
    skip: int
    limit: int


class StatsResponse(BaseModel):
    """Statistics response schema."""
    total_transactions: int
    total_anomalies: int
    average_risk_score: float
    critical_anomalies: int
    high_anomalies: int
    medium_anomalies: int
    low_anomalies: int


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str = "ok"
