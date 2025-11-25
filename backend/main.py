from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .database import init_db, close_db
from .logger import setup_logger
from .exceptions import exception_handlers
from .models import HealthCheck

# Import routers
from .routers import transactions, vehicles, anomalies, stats, auth

# Setup logger
logger = setup_logger(
    level=settings.log_level,
    log_format=settings.log_format,
    log_file=settings.log_file
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address) if settings.rate_limit_enabled else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Advanced fuel fraud detection system for construction, transport, and field-service companies",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add rate limiting
if settings.rate_limit_enabled and limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
for exc_class, handler in exception_handlers.items():
    app.add_exception_handler(exc_class, handler)

# Register API routers (workers and projects removed)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(transactions.router, prefix=settings.api_v1_prefix)
app.include_router(vehicles.router, prefix=settings.api_v1_prefix)
app.include_router(anomalies.router, prefix=settings.api_v1_prefix)
app.include_router(stats.router, prefix=settings.api_v1_prefix)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "documentation": "/api/docs"
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns application health status.
    """
    return HealthCheck(
        status="healthy",
        version=settings.app_version,
        database="ok"
    )


# Logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests."""
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown"
        }
    )
    response = await call_next(request)
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code
        }
    )
    return response
