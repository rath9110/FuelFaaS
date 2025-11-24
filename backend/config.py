from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration using Pydantic Settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "FuelGuard AI"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # API
    api_v1_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Database
    database_url: str = "sqlite:///./fuelguard.db"
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    
    # Redis
    redis_url: Optional[str] = None
    redis_enabled: bool = False
    
    # JWT Authentication
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_STRONG_RANDOM_KEY"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    log_file: Optional[str] = None
    
    # Email (for notifications)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    email_enabled: bool = False
    
    # Business Logic
    max_transactions_per_day_per_vehicle: int = 3
    price_anomaly_threshold_percent: float = 20.0
    double_dip_minutes: int = 30
    geofence_buffer_km: float = 15.0
    
    # Export
    max_export_records: int = 10000
    
    @property
    def database_url_async(self) -> str:
        """Convert sync database URL to async version."""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif self.database_url.startswith("sqlite"):
            return self.database_url.replace("sqlite", "sqlite+aiosqlite")
        return self.database_url


# Global settings instance
settings = Settings()
