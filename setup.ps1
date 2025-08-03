#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Vessel Guard Platform Setup Script
.DESCRIPTION
    This script sets up the complete Vessel Guard development environment including:
    - Node.js and npm dependencies
    - Python environment and backend dependencies
    - Database setup and migrations
    - Docker configuration
    - Development tools and scripts
.PARAMETER Environment
    Target environment: 'development', 'staging', or 'production'
.PARAMETER SkipDocker
    Skip Docker setup if already configured
.PARAMETER SkipDatabase
    Skip database setup if already configured
.EXAMPLE
    .\setup.ps1
    .\setup.ps1 -Environment development -SkipDocker
#>

param(
    [Parameter()]
    [ValidateSet('development', 'staging', 'production')]
    [string]$Environment = 'development',
    
    [Parameter()]
    [switch]$SkipDocker,
    
    [Parameter()]
    [switch]$SkipDatabase,
    
    [Parameter()]
    [switch]$Verbose
)

# Error handling
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param($Message, $Color = $Reset)
    Write-Host "$Color$Message$Reset"
}

function Write-Step {
    param($Message)
    Write-ColorOutput "🔹 $Message" $Blue
}

function Write-Success {
    param($Message)
    Write-ColorOutput "✅ $Message" $Green
}

function Write-Warning {
    param($Message)
    Write-ColorOutput "⚠️  $Message" $Yellow
}

function Write-Error {
    param($Message)
    Write-ColorOutput "❌ $Message" $Red
}

function Test-Command {
    param($Command)
    try {
        & $Command --version 2>$null >$null
        return $true
    } catch {
        return $false
    }
}

function Install-NodeDependencies {
    Write-Step "Installing Node.js dependencies..."
    
    # Check if Node.js is installed
    if (!(Test-Command "node")) {
        Write-Error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    }
    
    # Check Node version
    $nodeVersion = (node --version) -replace 'v', ''
    if ([version]$nodeVersion -lt [version]"18.0.0") {
        Write-Error "Node.js version 18+ is required. Current version: $nodeVersion"
        exit 1
    }
    
    Write-Success "Node.js version $nodeVersion detected"
    
    # Install root dependencies
    npm install
    
    # Install frontend dependencies
    Write-Step "Installing frontend dependencies..."
    Set-Location "apps/frontend"
    npm install
    Set-Location "../.."
    
    Write-Success "Node.js dependencies installed successfully"
}

function Install-PythonDependencies {
    Write-Step "Setting up Python environment..."
    
    # Check if Python is installed
    if (!(Test-Command "python")) {
        Write-Error "Python is not installed. Please install Python 3.9+ from https://python.org/"
        exit 1
    }
    
    # Check Python version
    $pythonVersion = (python --version) -replace 'Python ', ''
    if ([version]$pythonVersion -lt [version]"3.9.0") {
        Write-Error "Python version 3.9+ is required. Current version: $pythonVersion"
        exit 1
    }
    
    Write-Success "Python version $pythonVersion detected"
    
    # Create virtual environment if it doesn't exist
    Set-Location "apps/backend"
    
    if (!(Test-Path "venv")) {
        Write-Step "Creating Python virtual environment..."
        python -m venv venv
    }
    
    # Activate virtual environment
    Write-Step "Activating virtual environment..."
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        & "venv/Scripts/Activate.ps1"
    } else {
        & "venv/bin/activate"
    }
    
    # Install Python dependencies
    Write-Step "Installing Python dependencies..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    
    Set-Location "../.."
    Write-Success "Python environment setup completed"
}

function Setup-Database {
    if ($SkipDatabase) {
        Write-Warning "Skipping database setup as requested"
        return
    }
    
    Write-Step "Setting up database..."
    
    # Check if database file exists
    $dbPath = "apps/backend/vessel_guard_dev.db"
    if (Test-Path $dbPath) {
        Write-Warning "Database already exists at $dbPath"
        $response = Read-Host "Do you want to reset the database? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Remove-Item $dbPath -Force
            Write-Step "Database reset"
        }
    }
    
    # Run database migrations
    Write-Step "Running database migrations..."
    Set-Location "apps/backend"
    
    # Ensure alembic is configured
    if (!(Test-Path "alembic.ini")) {
        Write-Error "Alembic configuration not found. Database setup incomplete."
        Set-Location "../.."
        exit 1
    }
    
    # Run migrations
    python -m alembic upgrade head
    
    # Seed database if script exists
    if (Test-Path "scripts/seed_db.py") {
        Write-Step "Seeding database with initial data..."
        python scripts/seed_db.py
    }
    
    Set-Location "../.."
    Write-Success "Database setup completed"
}

function Setup-Docker {
    if ($SkipDocker) {
        Write-Warning "Skipping Docker setup as requested"
        return
    }
    
    Write-Step "Setting up Docker environment..."
    
    # Check if Docker is installed
    if (!(Test-Command "docker")) {
        Write-Warning "Docker is not installed. Please install Docker Desktop from https://docker.com/"
        Write-Warning "You can run the application without Docker using npm run dev"
        return
    }
    
    # Check if Docker is running
    try {
        docker ps 2>$null >$null
        Write-Success "Docker is running"
    } catch {
        Write-Warning "Docker is not running. Please start Docker Desktop"
        return
    }
    
    # Build Docker images for development
    Write-Step "Building Docker images..."
    docker-compose -f docker-compose.dev.yml build
    
    Write-Success "Docker setup completed"
}

function Setup-Environment {
    Write-Step "Setting up environment configuration..."
    
    # Copy environment files if they don't exist
    $backendEnvPath = "apps/backend/.env"
    $backendEnvExample = "apps/backend/dev.env"
    
    if (!(Test-Path $backendEnvPath) -and (Test-Path $backendEnvExample)) {
        Copy-Item $backendEnvExample $backendEnvPath
        Write-Success "Backend environment file created from template"
        Write-Warning "Please review and update $backendEnvPath with your configuration"
    }
    
    # Frontend environment (Next.js uses .env.local)
    $frontendEnvPath = "apps/frontend/.env.local"
    if (!(Test-Path $frontendEnvPath)) {
        @"
# Vessel Guard Frontend Environment Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Vessel Guard
NEXT_PUBLIC_VERSION=1.0.0
"@ | Out-File -FilePath $frontendEnvPath -Encoding UTF8
        Write-Success "Frontend environment file created"
    }
    
    Write-Success "Environment configuration completed"
}

function Setup-DevelopmentTools {
    Write-Step "Setting up development tools..."
    
    # Install pre-commit hooks if available
    if (Test-Path ".pre-commit-config.yaml") {
        if (Test-Command "pre-commit") {
            pre-commit install
            Write-Success "Pre-commit hooks installed"
        } else {
            Write-Warning "pre-commit not found. Install with: pip install pre-commit"
        }
    }
    
    # Setup VS Code workspace if available
    if (Test-Path "vessel-guard.code-workspace") {
        Write-Success "VS Code workspace file available"
        Write-ColorOutput "💡 Open the workspace with: code vessel-guard.code-workspace" $Blue
    }
    
    Write-Success "Development tools setup completed"
}

function Show-CompletionMessage {
    Write-ColorOutput "`n🎉 Vessel Guard Platform Setup Complete!" $Green
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $Green
    
    Write-ColorOutput "`n📋 Next Steps:" $Blue
    Write-ColorOutput "1. Review environment configuration files:" $Reset
    Write-ColorOutput "   • apps/backend/.env" $Yellow
    Write-ColorOutput "   • apps/frontend/.env.local" $Yellow
    
    Write-ColorOutput "`n2. Start the development servers:" $Reset
    Write-ColorOutput "   • Full stack: npm run dev" $Yellow
    Write-ColorOutput "   • With Docker: npm run dev:full" $Yellow
    Write-ColorOutput "   • Backend only: npm run dev:backend" $Yellow
    Write-ColorOutput "   • Frontend only: npm run dev:frontend" $Yellow
    
    Write-ColorOutput "`n3. Access the application:" $Reset
    Write-ColorOutput "   • Frontend: http://localhost:3000" $Yellow
    Write-ColorOutput "   • Backend API: http://localhost:8000" $Yellow
    Write-ColorOutput "   • API Docs: http://localhost:8000/docs" $Yellow
    
    Write-ColorOutput "`n4. Run tests:" $Reset
    Write-ColorOutput "   • All tests: npm test" $Yellow
    Write-ColorOutput "   • Backend tests: npm run test:backend" $Yellow
    Write-ColorOutput "   • Frontend tests: npm run test:frontend" $Yellow
    
    Write-ColorOutput "`n📚 Documentation:" $Reset
    Write-ColorOutput "   • README.md - Project overview" $Yellow
    Write-ColorOutput "   • CONTRIBUTING.md - Development guidelines" $Yellow
    Write-ColorOutput "   • docs/ - Technical documentation" $Yellow
    
    Write-ColorOutput "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $Green
}

# Main execution
try {
    Write-ColorOutput "`n🚀 Vessel Guard Platform Setup" $Green
    Write-ColorOutput "Environment: $Environment" $Blue
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $Blue
    
    # Store original location
    $originalLocation = Get-Location
    
    # Run setup steps
    Install-NodeDependencies
    Install-PythonDependencies
    Setup-Environment
    Setup-Database
    Setup-Docker
    Setup-DevelopmentTools
    
    # Return to original location
    Set-Location $originalLocation
    
    # Show completion message
    Show-CompletionMessage
    
} catch {
    Write-Error "Setup failed: $($_.Exception.Message)"
    Write-ColorOutput "❌ Please check the error above and run the setup script again." $Red
    exit 1
}
