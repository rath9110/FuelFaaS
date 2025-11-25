# Quick Start Script for FuelGuard AI
# This script bypasses environment file issues and starts the services directly

Write-Host "🚀 FuelGuard AI Quick Start"  -ForegroundColor Cyan
Write-Host ""

# Set environment variables directly
$env:DATABASE_URL = "sqlite+aiosqlite:///./fuelguard.db"
$env:SECRET_KEY = "development-secret-key-change-in-production"
$env:DEBUG = "true"
$env:ALLOWED_ORIGINS = "http://localhost:3000;http://localhost:8001"
$env:API_V1_PREFIX = "/api/v1"

Write-Host "📦 Step 1: Creating database..." -ForegroundColor Yellow

# Create tables directly with Python
python -c @"
import asyncio
from backend.database import Base, engine
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Database tables created!')

asyncio.run(create_tables())
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Database creation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🌱 Step 2: Seeding sample data..." -ForegroundColor Yellow
python seed_database.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Seeding failed, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Step 3: Starting backend server..." -ForegroundColor Yellow
Write-Host "Backend will be available at: http://localhost:8001" -ForegroundColor Green
Write-Host "API docs: http://localhost:8001/api/docs" -ForegroundColor Green
Write-Host ""

# Start backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$env:DATABASE_URL='sqlite+aiosqlite:///./fuelguard.db'; uvicorn backend.main:app --reload --port 8001"

Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🎨 Step 4: Starting frontend..." -ForegroundColor Yellow
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Green
Write-Host ""

# Check if node_modules exists
if (-Not (Test-Path "frontend/node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    cd frontend
    npm install
    cd ..
}

# Start frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD/frontend'; npm run dev"

Write-Host ""
Write-Host "✨ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Sample Login Credentials:" -ForegroundColor Cyan
Write-Host "   Username: admin"  -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access the application:"  -ForegroundColor Cyan
Write-Host "   Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8001/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open dashboard in browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "http://localhost:3000"
