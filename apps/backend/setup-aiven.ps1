# Vessel Guard Backend Setup Script for Aiven PostgreSQL
# This script sets up the backend environment for production with Aiven database

param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipVenv,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipDeps,
    
    [Parameter(Mandatory=$false)]
    [switch]$TestConnection
)

$ErrorActionPreference = "Stop"

Write-Host "=== Vessel Guard Backend Setup for Aiven PostgreSQL ===" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow

# Check if we're in the correct directory
if (-not (Test-Path "app\main.py")) {
    Write-Error "Please run this script from the backend directory"
    exit 1
}

# 1. Set up Python virtual environment
if (-not $SkipVenv) {
    Write-Host "`n1. Setting up Python virtual environment..." -ForegroundColor Green
    
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
    }
    
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
}

# 2. Install dependencies
if (-not $SkipDeps) {
    Write-Host "`n2. Installing dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
}

# 3. Set up environment file
Write-Host "`n3. Setting up environment configuration..." -ForegroundColor Green

if ($Environment -eq "development") {
    if (Test-Path ".env.development") {
        Write-Host "Copying development environment file..." -ForegroundColor Yellow
        Copy-Item ".env.development" ".env" -Force
    }
} else {
    Write-Host "Using production environment file (already configured for Aiven)..." -ForegroundColor Yellow
}

# 4. Test database connection
if ($TestConnection) {
    Write-Host "`n4. Testing database connection..." -ForegroundColor Green
    python init_db.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database connection successful!" -ForegroundColor Green
    } else {
        Write-Host "Database connection failed. Please check your configuration." -ForegroundColor Red
        exit 1
    }
}

# 5. Initialize database
Write-Host "`n5. Initializing database..." -ForegroundColor Green
Write-Host "Running database initialization..." -ForegroundColor Yellow
python init_db.py

# 6. Run database migrations
Write-Host "`n6. Running database migrations..." -ForegroundColor Green
Write-Host "Generating initial migration..." -ForegroundColor Yellow
alembic revision --autogenerate -m "Initial migration"

Write-Host "Running migrations..." -ForegroundColor Yellow
alembic upgrade head

# 7. Final setup verification
Write-Host "`n7. Verifying setup..." -ForegroundColor Green

# Check if server starts
Write-Host "Testing server startup..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WindowStyle Hidden -PassThru | ForEach-Object { 
    $process = $_
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "Server started successfully!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Server health check failed, but this might be normal if health endpoint is not implemented yet." -ForegroundColor Yellow
    }
    
    Stop-Process -Id $process.Id -Force
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Your Vessel Guard backend is now configured for Aiven PostgreSQL!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Update Redis configuration for production" -ForegroundColor White
Write-Host "2. Configure email settings in .env" -ForegroundColor White
Write-Host "3. Update CORS origins for your frontend domain" -ForegroundColor White
Write-Host "4. Generate a secure SECRET_KEY for production" -ForegroundColor White
Write-Host "`nTo start the server:" -ForegroundColor Yellow
Write-Host "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
