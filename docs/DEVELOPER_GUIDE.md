# Vessel Guard Developer Guide

## 🛠️ **Complete Development and Deployment Guide**

This guide provides comprehensive instructions for developers, DevOps engineers, and system administrators working with the Vessel Guard platform. From local development to production deployment, this documentation covers everything you need to know.

---

## 🚀 **Quick Start**

### **Prerequisites**
```bash
# Required Software
- Node.js 18+ (Frontend)
- Python 3.12+ (Backend)
- PostgreSQL 15+ (Database)
- Redis 7+ (Caching)
- Docker & Docker Compose (Containerization)
- Git (Version Control)

# Recommended Tools
- VS Code with extensions
- Postman (API testing)
- pgAdmin (Database management)
- Redis Commander (Cache management)
```

### **One-Command Setup**
```bash
# Clone and start the entire platform
git clone https://github.com/vessel-guard/platform.git
cd vessel-guard
./setup.ps1  # Windows
# or
./setup.sh  # Linux/macOS

# Platform will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🏗️ **Architecture Overview**

### **System Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│   Port 3000     │    │   Port 8000     │    │   Port 5432     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │     Redis       │             │
         │              │   (Caching)     │             │
         │              │   Port 6379     │             │
         │              └─────────────────┘             │
         │                                              │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   File Storage  │    │   Monitoring    │
│   (nginx/Azure) │    │   (Azure Blob)  │    │   (Prometheus)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Technology Stack**

#### **Frontend (Next.js 14)**
```typescript
Core Technologies:
├── React 18 with TypeScript
├── Next.js 14 (App Router)
├── Tailwind CSS for styling
├── Zustand for state management
├── React Query for data fetching
├── React Hook Form + Zod validation
├── Radix UI components
└── Framer Motion animations

Development Tools:
├── ESLint + Prettier
├── Jest + React Testing Library
├── Playwright (E2E testing)
├── Storybook (component docs)
└── Turbo for monorepo management
```

#### **Backend (FastAPI + Python)**
```python
Core Technologies:
├── FastAPI with Pydantic v2
├── SQLAlchemy 2.0 ORM
├── Alembic database migrations
├── PostgreSQL with asyncpg
├── Redis for caching/sessions
├── Celery for background tasks
├── JWT authentication
└── OpenAPI/Swagger docs

Development Tools:
├── Poetry for dependency management
├── Pytest for testing
├── Black + isort formatting
├── mypy type checking
├── Bandit security scanning
└── Ruff linting
```

#### **Database & Infrastructure**
```sql
Database:
├── PostgreSQL 15+ (primary database)
├── Redis 7+ (caching & sessions)
├── Azure Blob Storage (file storage)
└── Elasticsearch (search & analytics)

Infrastructure:
├── Docker containers
├── Azure Container Apps
├── Azure Application Gateway
├── Azure Monitor & Log Analytics
└── GitHub Actions CI/CD
```

---

## 💻 **Local Development Setup**

### **Environment Configuration**

#### **Backend Environment**
Create `apps/backend/.env`:
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/vessel_guard
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=vessel_guard
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application Settings
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=30

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# CORS Settings
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Email Configuration (for development)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@vessel-guard.com

# File Storage
AZURE_STORAGE_CONNECTION_STRING=your-azure-storage-connection
AZURE_STORAGE_CONTAINER=vessel-guard-files

# External APIs
OPENAI_API_KEY=your-openai-key  # For AI features
MAPS_API_KEY=your-maps-key      # For location services
```

#### **Frontend Environment**
Create `apps/frontend/.env.local`:
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_API_DOCS_URL=http://localhost:8000/docs

# Environment
NODE_ENV=development
NEXT_PUBLIC_ENV=development

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

# Analytics (optional)
NEXT_PUBLIC_GA_ID=your-google-analytics-id
NEXT_PUBLIC_HOTJAR_ID=your-hotjar-id

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_DARK_MODE=true
```

### **Database Setup**

#### **PostgreSQL Installation & Configuration**
```bash
# Install PostgreSQL
# Windows (using Chocolatey)
choco install postgresql

# macOS (using Homebrew)
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
# Windows
net start postgresql-x64-15

# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

#### **Database Initialization**
```bash
# Create database and user
psql -U postgres
CREATE DATABASE vessel_guard;
CREATE USER vessel_guard_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE vessel_guard TO vessel_guard_user;
\q

# Run migrations
cd apps/backend
python -m alembic upgrade head

# Seed initial data
python -m app.db.init_db
```

### **Development Server Startup**

#### **Backend Development**
```bash
cd apps/backend

# Install dependencies
pip install -r requirements.txt

# Alternative: Using Poetry
poetry install
poetry shell

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the dev script
python dev.py

# Server will be available at:
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

#### **Frontend Development**
```bash
cd apps/frontend

# Install dependencies
npm install
# or
yarn install

# Start development server
npm run dev
# or
yarn dev

# Server will be available at:
# App: http://localhost:3000
```

#### **Full Stack Development**
```bash
# Start everything with Docker Compose
docker-compose -f docker-compose.dev.yml up

# Or use the development script
npm run dev:all

# This starts:
# - PostgreSQL on port 5432
# - Redis on port 6379
# - Backend on port 8000
# - Frontend on port 3000
```

---

## 🧪 **Testing**

### **Backend Testing**

#### **Test Configuration**
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    security: Security tests
```

#### **Running Tests**
```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m performance   # Performance tests only

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_calculations.py

# Run specific test function
pytest tests/test_calculations.py::test_pressure_vessel_calculation

# Parallel testing
pytest -n 4  # Run with 4 workers
```

#### **Test Database Setup**
```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from app.api.dependencies import get_db

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/vessel_guard_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

### **Frontend Testing**

#### **Jest Configuration**
```javascript
// jest.config.js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/pages/(.*)$': '<rootDir>/src/pages/$1',
    '^@/lib/(.*)$': '<rootDir>/src/lib/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
```

#### **Running Frontend Tests**
```bash
# Unit and integration tests
npm run test
npm run test:watch
npm run test:coverage

# E2E tests with Playwright
npm run test:e2e
npm run test:e2e:headed  # With browser UI

# Visual regression tests
npm run test:visual

# Component testing with Storybook
npm run storybook
npm run test:storybook
```

#### **E2E Test Example**
```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[data-testid=email]', 'test@vessel-guard.com');
    await page.fill('[data-testid=password]', 'TestPassword123');
    await page.click('[data-testid=login-button]');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid=user-menu]')).toBeVisible();
  });

  test('should show validation errors for invalid input', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[data-testid=email]', 'invalid-email');
    await page.click('[data-testid=login-button]');
    
    await expect(page.locator('[data-testid=email-error]')).toContainText('Invalid email format');
  });
});
```

---

## 🚀 **Deployment**

### **Production Environment Setup**

#### **Azure Container Apps Deployment**

**1. Infrastructure Setup**
```bash
# Create resource group
az group create --name vessel-guard-prod --location eastus

# Create container registry
az acr create --resource-group vessel-guard-prod \
              --name vesselguardacr \
              --sku Basic \
              --admin-enabled true

# Create container app environment
az containerapp env create \
  --name vessel-guard-env \
  --resource-group vessel-guard-prod \
  --location eastus
```

**2. Database Setup**
```bash
# Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group vessel-guard-prod \
  --name vessel-guard-db \
  --location eastus \
  --admin-user vesselguard \
  --admin-password SecurePassword123! \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 15

# Create database
az postgres flexible-server db create \
  --resource-group vessel-guard-prod \
  --server-name vessel-guard-db \
  --database-name vessel_guard
```

**3. Redis Cache Setup**
```bash
# Create Redis cache
az redis create \
  --resource-group vessel-guard-prod \
  --name vessel-guard-cache \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

#### **Container Image Building**

**Backend Dockerfile**
```dockerfile
# apps/backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**
```dockerfile
# apps/frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
```

### **CI/CD Pipeline**

#### **GitHub Actions Workflow**
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.12'
  NODE_VERSION: '18'
  REGISTRY: vesselguardacr.azurecr.io

jobs:
  # Backend tests
  backend-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./apps/backend
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: vessel_guard_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run unit tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/vessel_guard_test
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret-key
        ENVIRONMENT: test
      run: |
        python -m pytest tests/unit/ -v --cov=app --cov-report=xml
    
    - name: Run integration tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/vessel_guard_test
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret-key
        ENVIRONMENT: test
      run: |
        python -m pytest tests/integration/ -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./apps/backend/coverage.xml

  # Frontend tests
  frontend-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./apps/frontend

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
        cache-dependency-path: apps/frontend/package-lock.json
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run unit tests
      run: npm run test:coverage
    
    - name: Install Playwright
      run: npx playwright install --with-deps
    
    - name: Run E2E tests
      run: npm run test:e2e
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: apps/frontend/playwright-report/

  # Security scanning
  security-scan:
    runs-on: ubuntu-latest
    needs: [backend-test, frontend-test]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python for security scanning
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install security tools
      run: |
        pip install bandit safety semgrep
    
    - name: Run Bandit
      run: |
        bandit -r apps/backend/app/ -f json -o bandit-report.json
      continue-on-error: true
    
    - name: Run Safety
      run: |
        safety check --json --output safety-report.json
      continue-on-error: true
    
    - name: Run Semgrep
      run: |
        semgrep --config=auto --json --output=semgrep-report.json apps/
      continue-on-error: true
    
    - name: Upload security reports as artifacts
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json
          semgrep-report.json

  # Build and push Docker images
  build-and-push:
    runs-on: ubuntu-latest
    needs: [backend-test, frontend-test, security-scan]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Azure Container Registry
      uses: azure/docker-login@v1
      with:
        login-server: ${{ env.REGISTRY }}
        username: ${{ secrets.ACR_USERNAME }}
        password: ${{ secrets.ACR_PASSWORD }}
    
    - name: Build and push backend image
      working-directory: ./apps/backend
      run: |
        docker build -t ${{ env.REGISTRY }}/vessel-guard-backend:${{ github.sha }} .
        docker push ${{ env.REGISTRY }}/vessel-guard-backend:${{ github.sha }}
    
    - name: Build and push frontend image
      working-directory: ./apps/frontend
      run: |
        docker build -t ${{ env.REGISTRY }}/vessel-guard-frontend:${{ github.sha }} .
        docker push ${{ env.REGISTRY }}/vessel-guard-frontend:${{ github.sha }}

  # Deploy to staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-and-push
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy to staging
      run: |
        # Update container apps with new images
        az containerapp update \
          --name vessel-guard-backend-staging \
          --resource-group vessel-guard-staging \
          --image ${{ env.REGISTRY }}/vessel-guard-backend:${{ github.sha }}
        
        az containerapp update \
          --name vessel-guard-frontend-staging \
          --resource-group vessel-guard-staging \
          --image ${{ env.REGISTRY }}/vessel-guard-frontend:${{ github.sha }}
    
    - name: Run staging smoke tests
      run: |
        # Wait for deployment
        sleep 60
        
        # Test health endpoints
        curl -f https://staging-api.vessel-guard.com/api/v1/health
        curl -f https://staging.vessel-guard.com/
    
    - name: Notify deployment status
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: "Staging deployment ${{ job.status }}: ${{ github.sha }}"
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      if: always() && secrets.SLACK_WEBHOOK

  # Deploy to production
  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Blue-Green Production Deployment
      run: |
        # Deploy to green environment
        az containerapp update \
          --name vessel-guard-backend-green \
          --resource-group vessel-guard-prod \
          --image ${{ env.REGISTRY }}/vessel-guard-backend:${{ github.sha }}
        
        az containerapp update \
          --name vessel-guard-frontend-green \
          --resource-group vessel-guard-prod \
          --image ${{ env.REGISTRY }}/vessel-guard-frontend:${{ github.sha }}
        
        # Health check
        sleep 60
        curl -f https://green-api.vessel-guard.com/api/v1/health
        
        # Switch traffic to green
        # (This would typically involve updating load balancer rules)
        echo "Switch traffic to green environment"
        
        # Run post-deployment verification
        curl -f https://api.vessel-guard.com/api/v1/health
        curl -f https://api.vessel-guard.com/api/v1/status
    
    - name: Notify deployment status
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: "Production deployment ${{ job.status }}: ${{ github.sha }}"
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      if: always() && secrets.SLACK_WEBHOOK
```

### **Environment Configuration**

#### **Production Environment Variables**
```bash
# Backend Production Environment
DATABASE_URL=postgresql://user:password@vessel-guard-db.postgres.database.azure.com:5432/vessel_guard
REDIS_URL=redis://vessel-guard-cache.redis.cache.windows.net:6380?ssl=true
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=your-production-storage-connection
AZURE_STORAGE_CONTAINER=vessel-guard-prod-files

# Email Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your-newrelic-key
PROMETHEUS_METRICS_ENABLED=true

# Security
CORS_ORIGINS=["https://vessel-guard.com","https://www.vessel-guard.com"]
TRUSTED_HOSTS=["vessel-guard.com","api.vessel-guard.com"]
```

---

## 🔧 **Configuration Management**

### **Application Configuration**

#### **Backend Configuration**
```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional, Any, Dict, Union

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Vessel Guard API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "vessel_guard"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    
    # File Storage
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: str = "vessel-guard-files"
    
    # External Services
    OPENAI_API_KEY: Optional[str] = None
    SENTRY_DSN: Optional[str] = None
    
    # Monitoring
    PROMETHEUS_METRICS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

#### **Frontend Configuration**
```typescript
// src/config/index.ts
interface Config {
  api: {
    baseUrl: string;
    timeout: number;
  };
  auth: {
    tokenKey: string;
    refreshKey: string;
  };
  features: {
    analytics: boolean;
    darkMode: boolean;
    chat: boolean;
  };
  monitoring: {
    sentry: {
      dsn?: string;
      environment: string;
    };
    hotjar: {
      id?: string;
    };
  };
}

const config: Config = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    timeout: 30000,
  },
  auth: {
    tokenKey: 'vessel_guard_token',
    refreshKey: 'vessel_guard_refresh_token',
  },
  features: {
    analytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
    darkMode: process.env.NEXT_PUBLIC_ENABLE_DARK_MODE === 'true',
    chat: process.env.NEXT_PUBLIC_ENABLE_CHAT === 'true',
  },
  monitoring: {
    sentry: {
      dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
      environment: process.env.NEXT_PUBLIC_ENV || 'development',
    },
    hotjar: {
      id: process.env.NEXT_PUBLIC_HOTJAR_ID,
    },
  },
};

export default config;
```

### **Database Migrations**

#### **Alembic Configuration**
```python
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db.base import Base
from app.core.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=Base.metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### **Creating Migrations**
```bash
# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Run migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1

# Show migration history
alembic history

# Show current revision
alembic current
```

---

## 📊 **Monitoring and Observability**

### **Application Monitoring**

#### **Prometheus Metrics**
```python
# app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
import time

# Application metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users_total',
    'Number of active users'
)

CALCULATION_COUNT = Counter(
    'calculations_total',
    'Total calculations performed',
    ['calculation_type', 'status']
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Active database connections'
)

# Middleware for automatic metrics collection
class PrometheusMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=path,
                    status=status
                ).inc()
                
                duration = time.time() - start_time
                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
```

#### **Structured Logging**
```python
# app/core/logging_config.py
import logging
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "organization_id"):
            log_entry["organization_id"] = record.organization_id
        
        # Add exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )
    
    # Set JSON formatter for production
    if settings.ENVIRONMENT == "production":
        for handler in logging.getLogger().handlers:
            handler.setFormatter(JSONFormatter())
```

### **Health Checks**

#### **Comprehensive Health Monitoring**
```python
# app/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis import Redis
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependency verification."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": 0  # Would measure actual time
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "response_time_ms": 0
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # External services check
    health_status["checks"]["external_services"] = await check_external_services()
    
    return health_status

async def check_external_services():
    """Check external service availability."""
    services = {}
    
    # Example: Check OpenAI API
    if settings.OPENAI_API_KEY:
        try:
            # Would make actual API call
            services["openai"] = {"status": "healthy"}
        except:
            services["openai"] = {"status": "unhealthy"}
    
    return services
```

### **Error Tracking**

#### **Sentry Integration**
```python
# app/core/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def setup_sentry():
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
        )
```

---

## 🤝 **Contributing**

### **Development Workflow**

#### **Git Workflow**
```bash
# Clone repository
git clone https://github.com/vessel-guard/platform.git
cd vessel-guard

# Create feature branch
git checkout -b feature/new-calculation-engine

# Make changes and commit
git add .
git commit -m "feat: add new pressure vessel calculation engine"

# Push and create pull request
git push origin feature/new-calculation-engine
```

#### **Commit Message Convention**
```
type(scope): description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks

Examples:
feat(calculations): add ASME VIII Div 2 support
fix(auth): resolve token expiration issue
docs(api): update endpoint documentation
test(vessels): add unit tests for vessel creation
```

### **Code Quality Standards**

#### **Python Code Standards**
```python
# Use type hints
def calculate_pressure_vessel(
    diameter: float,
    thickness: float,
    material: str,
    pressure: float
) -> Dict[str, Any]:
    """
    Calculate pressure vessel parameters.
    
    Args:
        diameter: Inside diameter in inches
        thickness: Wall thickness in inches  
        material: Material specification
        pressure: Design pressure in psi
        
    Returns:
        Dictionary containing calculation results
        
    Raises:
        ValueError: If input parameters are invalid
    """
    if diameter <= 0:
        raise ValueError("Diameter must be positive")
    
    # Implementation here
    return {"status": "compliant", "safety_factor": 3.2}

# Use docstrings for all functions and classes
class PressureVessel:
    """Represents a pressure vessel for analysis."""
    
    def __init__(self, tag_number: str, diameter: float):
        self.tag_number = tag_number
        self.diameter = diameter
```

#### **TypeScript Code Standards**
```typescript
// Use explicit types
interface VesselData {
  id: number;
  tagNumber: string;
  diameter: number;
  thickness: number;
  material: string;
}

// Use proper error handling
async function createVessel(data: VesselData): Promise<Vessel> {
  try {
    const response = await api.post('/vessels', data);
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new VesselCreationError(error.message);
    }
    throw error;
  }
}

// Use React best practices
export const VesselForm: React.FC<VesselFormProps> = ({ onSubmit }) => {
  const [vessel, setVessel] = useState<VesselData>({
    id: 0,
    tagNumber: '',
    diameter: 0,
    thickness: 0,
    material: '',
  });

  const handleSubmit = useCallback(async (event: FormEvent) => {
    event.preventDefault();
    await onSubmit(vessel);
  }, [vessel, onSubmit]);

  return (
    <form onSubmit={handleSubmit}>
      {/* Form implementation */}
    </form>
  );
};
```

### **Pull Request Process**

#### **PR Requirements**
```markdown
## Pull Request Checklist

### Code Quality
- [ ] Code follows style guidelines
- [ ] Type hints added (Python) / Types defined (TypeScript)
- [ ] Docstrings/comments added for complex logic
- [ ] No commented-out code or debug statements

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated (if applicable)
- [ ] All tests pass locally
- [ ] Code coverage maintained or improved

### Documentation
- [ ] README updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] Changelog updated

### Security
- [ ] No sensitive data in code
- [ ] Security implications considered
- [ ] Input validation added

### Performance
- [ ] Performance implications considered
- [ ] Database queries optimized
- [ ] Caching strategy implemented (if applicable)
```

#### **Review Process**
1. **Automated Checks**: CI/CD pipeline runs all tests
2. **Peer Review**: At least one team member review
3. **Security Review**: For security-sensitive changes
4. **Performance Review**: For performance-critical changes
5. **Documentation Review**: For user-facing changes

---

## 📞 **Support and Resources**

### **Developer Resources**
- **API Documentation**: [developers.vessel-guard.com](https://developers.vessel-guard.com)
- **GitHub Repository**: [github.com/vessel-guard/platform](https://github.com/vessel-guard/platform)
- **Issue Tracker**: [github.com/vessel-guard/platform/issues](https://github.com/vessel-guard/platform/issues)
- **Discord Community**: [discord.gg/vessel-guard](https://discord.gg/vessel-guard)

### **Support Channels**
- **Developer Forum**: [developers.vessel-guard.com/forum](https://developers.vessel-guard.com/forum)
- **Technical Support**: dev-support@vessel-guard.com
- **Architecture Questions**: architecture@vessel-guard.com
- **Security Issues**: security@vessel-guard.com

### **Additional Documentation**
- [Architecture Guide](ARCHITECTURE.md) - System architecture and design decisions
- [Security Guide](SECURITY.md) - Security best practices and guidelines
- [Performance Guide](PERFORMANCE.md) - Performance optimization strategies
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions

---

*This developer guide is maintained by the Vessel Guard engineering team. Last updated: December 2024*