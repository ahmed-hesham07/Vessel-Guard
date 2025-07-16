#!/usr/bin/env pwsh
# Fly.io Deployment Script for Vessel Guard Backend

Write-Host "Starting Fly.io deployment for Vessel Guard Backend..." -ForegroundColor Green

# Check if flyctl is installed
if (!(Get-Command "flyctl" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: flyctl is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "PowerShell: iwr https://fly.io/install.ps1 -useb | iex" -ForegroundColor Yellow
    exit 1
}

# Check if we're logged into Fly.io
$flyAuth = flyctl auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Not logged into Fly.io. Please run 'flyctl auth login' first." -ForegroundColor Red
    exit 1
}

Write-Host "Logged in as: $flyAuth" -ForegroundColor Green

# Check if fly.toml exists
if (!(Test-Path "fly.toml")) {
    Write-Host "Error: fly.toml not found. Please ensure you're in the correct directory." -ForegroundColor Red
    exit 1
}

# Create Fly.io app if it doesn't exist
Write-Host "Checking if Fly.io app exists..." -ForegroundColor Yellow
$appExists = flyctl apps list | Select-String "vessel-guard-backend"
if (!$appExists) {
    Write-Host "Creating Fly.io app..." -ForegroundColor Yellow
    flyctl apps create vessel-guard-backend --org personal
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create Fly.io app." -ForegroundColor Red
        exit 1
    }
}

# Set secrets from .env.fly
Write-Host "Setting Fly.io secrets..." -ForegroundColor Yellow
if (Test-Path ".env.fly") {
    $envVars = Get-Content ".env.fly" | Where-Object { $_ -notmatch "^\s*#" -and $_ -notmatch "^\s*$" }
    foreach ($line in $envVars) {
        if ($line -match "^([^=]+)=(.*)$") {
            $key = $matches[1]
            $value = $matches[2]
            
            # Skip certain variables that shouldn't be secrets
            if ($key -in @("APP_NAME", "ENVIRONMENT", "FLY_APP_NAME", "FLY_REGION")) {
                continue
            }
            
            Write-Host "Setting secret: $key" -ForegroundColor Cyan
            flyctl secrets set "$key=$value" --app vessel-guard-backend
        }
    }
}

# Create PostgreSQL database if it doesn't exist
Write-Host "Checking for PostgreSQL database..." -ForegroundColor Yellow
$dbExists = flyctl postgres list | Select-String "vessel-guard-db"
if (!$dbExists) {
    Write-Host "Creating PostgreSQL database..." -ForegroundColor Yellow
    flyctl postgres create --name vessel-guard-db --region sea --vm-size shared-cpu-1x --volume-size 3
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create PostgreSQL database." -ForegroundColor Red
        exit 1
    }
    
    # Attach database to app
    Write-Host "Attaching database to app..." -ForegroundColor Yellow
    flyctl postgres attach vessel-guard-db --app vessel-guard-backend
}

# Deploy the application
Write-Host "Deploying application..." -ForegroundColor Yellow
flyctl deploy --app vessel-guard-backend

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "Your app is available at: https://vessel-guard-backend.fly.dev" -ForegroundColor Green
    
    # Show app status
    Write-Host "App status:" -ForegroundColor Yellow
    flyctl status --app vessel-guard-backend
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Fly.io deployment completed!" -ForegroundColor Green
