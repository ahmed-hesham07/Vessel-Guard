# 🔧 Vessel Guard - Complete Setup Guide

This comprehensive guide covers all aspects of setting up, configuring, and deploying the Vessel Guard platform for development, staging, and production environments.

## 📑 Table of Contents

- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Docker Setup](#docker-setup)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## 🔧 Prerequisites

### System Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **OS** | Windows 10, macOS 10.15, Ubuntu 18.04 | Latest LTS versions | |
| **Node.js** | 18.0.0+ | 20.x LTS | Required for frontend |
| **Python** | 3.9+ | 3.11+ | Required for backend |
| **RAM** | 4GB | 8GB+ | For development |
| **Storage** | 5GB | 10GB+ | Includes dependencies |
| **Docker** | 20.0+ | Latest | Optional for development |

### Required Software

#### 1. Node.js & npm
```bash
# Install Node.js from https://nodejs.org/
node --version  # Should be 18.0.0+
npm --version   # Should be 8.0.0+
```

#### 2. Python & pip
```bash
# Install Python from https://python.org/
python --version  # Should be 3.9.0+
pip --version     # Should be 21.0+
```

#### 3. Git
```bash
# Install Git from https://git-scm.com/
git --version  # Should be 2.0+
```

#### 4. Docker (Optional)
```bash
# Install Docker from https://docker.com/
docker --version  # Should be 20.0+
docker-compose --version  # Should be 1.29+
```

## 🚀 Development Setup

### Quick Setup (Automated)

The fastest way to get started is using our setup script:

```powershell
# Windows PowerShell
.\setup.ps1

# With specific environment
.\setup.ps1 -Environment development

# Skip certain components
.\setup.ps1 -SkipDocker -SkipDatabase
```

```bash
# Linux/macOS
chmod +x setup.ps1
./setup.ps1
```

### Manual Setup (Step-by-Step)

If you prefer manual setup or need to troubleshoot:

#### 1. Clone Repository
```bash
git clone https://github.com/ahmed-hesham07/Vessel-Guard.git
cd Vessel-Guard
```

#### 2. Install Root Dependencies
```bash
npm install
```

#### 3. Setup Frontend
```bash
cd apps/frontend
npm install
cd ../..
```

#### 4. Setup Backend
```bash
cd apps/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

cd ../..
```

#### 5. Environment Configuration
```bash
# Copy environment templates
cp apps/backend/dev.env apps/backend/.env

# Create frontend environment
cat > apps/frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Vessel Guard
EOF
```

#### 6. Database Setup
```bash
cd apps/backend

# Run migrations
python -m alembic upgrade head

# Seed database (optional)
python scripts/seed_db.py

cd ../..
```

#### 7. Start Development Servers
```bash
# Start both frontend and backend
npm run dev

# Or individually:
npm run dev:frontend  # Port 3000
npm run dev:backend   # Port 8000
```

## ⚙️ Environment Configuration

### Backend Environment (`apps/backend/.env`)

```env
# Database Configuration
DATABASE_URL=sqlite:///./vessel_guard_dev.db
# For PostgreSQL: postgresql://user:password@localhost/vessel_guard

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email Configuration (Development)
EMAIL_SERVER_HOST=localhost
EMAIL_SERVER_PORT=1025
EMAIL_SERVER_USER=
EMAIL_SERVER_PASSWORD=
EMAIL_USE_TLS=false
EMAIL_FROM=noreply@vessel-guard.com

# File Storage
UPLOAD_DIRECTORY=uploads
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Engineering Standards
DEFAULT_UNITS=imperial  # or metric
ENABLE_ASME_VIII_DIV1=true
ENABLE_ASME_VIII_DIV2=true
ENABLE_ASME_B31_3=true
ENABLE_API_579=true
ENABLE_EN_13445=true

# Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/vessel_guard.log

# Development Settings
DEBUG=true
TESTING=false
```

### Frontend Environment (`apps/frontend/.env.local`)

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Application Settings
NEXT_PUBLIC_APP_NAME=Vessel Guard
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_COMPANY_NAME=Your Company

# Feature Flags
NEXT_PUBLIC_ENABLE_REGISTRATION=true
NEXT_PUBLIC_ENABLE_OAUTH=false
NEXT_PUBLIC_ENABLE_ANALYTICS=true

# UI Configuration
NEXT_PUBLIC_DEFAULT_THEME=light
NEXT_PUBLIC_ENABLE_DARK_MODE=true
NEXT_PUBLIC_ITEMS_PER_PAGE=20

# Development Settings
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_MOCK_API=false
```

### Production Environment

#### Production Backend (`.env.production`)
```env
# Database - Use PostgreSQL in production
DATABASE_URL=postgresql://user:password@db-host:5432/vessel_guard_prod

# Security - Strong secrets
SECRET_KEY=very-long-random-string-generated-securely
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS - Specific domains only
CORS_ORIGINS=https://your-domain.com

# Email - Real SMTP settings
EMAIL_SERVER_HOST=smtp.gmail.com
EMAIL_SERVER_PORT=587
EMAIL_SERVER_USER=your-email@gmail.com
EMAIL_SERVER_PASSWORD=your-app-password
EMAIL_USE_TLS=true
EMAIL_FROM=noreply@your-domain.com

# File Storage - Cloud storage
UPLOAD_DIRECTORY=/var/uploads
MAX_FILE_SIZE=52428800  # 50MB

# Background Tasks - Redis cluster
CELERY_BROKER_URL=redis://redis-cluster:6379/0
CELERY_RESULT_BACKEND=redis://redis-cluster:6379/0

# Production Settings
DEBUG=false
LOG_LEVEL=WARNING
LOG_FILE=/var/log/vessel_guard/app.log
```

#### Production Frontend (`.env.production`)
```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_WS_URL=wss://api.your-domain.com
NEXT_PUBLIC_APP_NAME=Vessel Guard
NEXT_PUBLIC_DEBUG=false
NEXT_PUBLIC_ENABLE_REGISTRATION=false  # Disable public registration
```

## 🗄️ Database Setup

### Development Database (SQLite)

SQLite is used by default for development - no additional setup required.

```bash
cd apps/backend

# Check current migration status
python -m alembic current

# Run all migrations
python -m alembic upgrade head

# Create new migration (if you made model changes)
python -m alembic revision --autogenerate -m "Description of changes"
```

### Production Database (PostgreSQL)

#### 1. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server

# macOS
brew install postgresql
```

#### 2. Create Database and User
```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database
CREATE DATABASE vessel_guard_prod;

-- Create user
CREATE USER vessel_guard_user WITH ENCRYPTED PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE vessel_guard_prod TO vessel_guard_user;

-- Exit
\q
```

#### 3. Update Environment
```env
DATABASE_URL=postgresql://vessel_guard_user:secure_password@localhost:5432/vessel_guard_prod
```

#### 4. Run Migrations
```bash
cd apps/backend
python -m alembic upgrade head
```

### Database Backup and Restore

#### SQLite
```bash
# Backup
cp apps/backend/vessel_guard_dev.db vessel_guard_backup_$(date +%Y%m%d).db

# Restore
cp vessel_guard_backup_20240101.db apps/backend/vessel_guard_dev.db
```

#### PostgreSQL
```bash
# Backup
pg_dump -h localhost -U vessel_guard_user vessel_guard_prod > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U vessel_guard_user vessel_guard_prod < backup_20240101.sql
```

## 🐳 Docker Setup

### Development with Docker

#### 1. Development Compose
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# Run in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

#### 2. Individual Services
```bash
# Backend only
docker-compose -f docker-compose.dev.yml up backend

# Frontend only
docker-compose -f docker-compose.dev.yml up frontend

# Database only
docker-compose -f docker-compose.dev.yml up postgres
```

### Production Docker Deployment

#### 1. Build Production Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
```

#### 2. Production Deployment
```bash
# Start production services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### 3. Scaling Services
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale with load balancer
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### 4. Health Checks
```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check frontend
curl http://localhost:3000

# Check all services
docker-compose exec backend python -c "from app.core.health import health_check; print(health_check())"
```

## 🚀 Production Deployment

### Cloud Deployment Options

#### 1. Azure Container Apps
```bash
# Login to Azure
az login

# Deploy using Azure Developer CLI
azd init
azd up
```

#### 2. AWS ECS
```bash
# Configure AWS CLI
aws configure

# Deploy using CDK or CloudFormation
npm run deploy:aws
```

#### 3. Google Cloud Run
```bash
# Configure gcloud
gcloud auth login

# Deploy services
gcloud run deploy vessel-guard-backend --source apps/backend
gcloud run deploy vessel-guard-frontend --source apps/frontend
```

#### 4. DigitalOcean App Platform
```bash
# Using doctl
doctl apps create vessel-guard-app.yaml
```

### Manual Server Deployment

#### 1. Server Setup (Ubuntu 20.04+)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip nodejs npm nginx postgresql redis

# Install PM2 for process management
sudo npm install -g pm2

# Create application user
sudo useradd -m -s /bin/bash vessel-guard
sudo usermod -aG sudo vessel-guard
```

#### 2. Application Deployment
```bash
# Clone repository
sudo -u vessel-guard git clone https://github.com/ahmed-hesham07/Vessel-Guard.git /home/vessel-guard/app
cd /home/vessel-guard/app

# Set up backend
cd apps/backend
sudo -u vessel-guard python3 -m venv venv
sudo -u vessel-guard venv/bin/pip install -r requirements.txt

# Set up frontend
cd ../frontend
sudo -u vessel-guard npm ci
sudo -u vessel-guard npm run build
cd ../..
```

#### 3. Process Management with PM2
```bash
# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'vessel-guard-backend',
      cwd: './apps/backend',
      script: 'venv/bin/python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'vessel-guard-frontend',
      cwd: './apps/frontend',
      script: 'npm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    }
  ]
};
EOF

# Start services
sudo -u vessel-guard pm2 start ecosystem.config.js

# Save PM2 configuration
sudo -u vessel-guard pm2 save

# Set up PM2 startup
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u vessel-guard --hp /home/vessel-guard
```

#### 4. Nginx Configuration
```nginx
# /etc/nginx/sites-available/vessel-guard
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # File uploads
    client_max_body_size 50M;
}

# Enable site
sudo ln -s /etc/nginx/sites-available/vessel-guard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use npx
npx kill-port 3000 8000
```

#### 2. Permission Errors (Windows)
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single script
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

#### 3. Python Virtual Environment Issues
```bash
# Remove corrupted environment
rm -rf apps/backend/venv

# Recreate
cd apps/backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### 4. Database Migration Errors
```bash
cd apps/backend

# Check migration status
python -m alembic current

# Reset database (development only)
rm vessel_guard_dev.db
python -m alembic upgrade head

# Force specific revision
python -m alembic downgrade <revision>
python -m alembic upgrade head
```

#### 5. Node Modules Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove and reinstall
rm -rf node_modules package-lock.json
npm install

# For frontend
cd apps/frontend
rm -rf node_modules package-lock.json .next
npm install
```

#### 6. Docker Issues
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Reset Docker volumes
docker-compose down -v
docker-compose up --build
```

### Performance Issues

#### 1. Backend Performance
```bash
# Monitor Python process
htop
ps aux | grep python

# Profile with cProfile
python -m cProfile -o profile.stats -m uvicorn app.main:app

# Monitor database queries
tail -f logs/vessel_guard.log | grep "SELECT"
```

#### 2. Frontend Performance
```bash
# Analyze bundle size
cd apps/frontend
npm run analyze

# Check for memory leaks
npm run dev -- --inspect

# Monitor build times
npm run build -- --profile
```

#### 3. Database Performance
```sql
-- PostgreSQL query analysis
EXPLAIN ANALYZE SELECT * FROM vessels WHERE organization_id = 1;

-- Check slow queries
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

### Logging and Debugging

#### 1. Backend Logging
```bash
# View real-time logs
tail -f apps/backend/logs/vessel_guard.log

# Search for errors
grep "ERROR" apps/backend/logs/vessel_guard.log

# Increase log level for debugging
# In .env: LOG_LEVEL=DEBUG
```

#### 2. Frontend Debugging
```bash
# Enable debug mode
# In .env.local: NEXT_PUBLIC_DEBUG=true

# Check browser console
# Open Developer Tools -> Console

# View Next.js build info
npm run build 2>&1 | grep -E "(warning|error)"
```

#### 3. Docker Debugging
```bash
# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute commands in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Inspect container
docker inspect vessel-guard_backend_1
```

## 🔒 Security Considerations

### Development Security
- Never commit `.env` files with real credentials
- Use strong, unique `SECRET_KEY` values
- Enable CORS only for necessary origins
- Use HTTPS in production

### Production Security
- Use environment variables for secrets
- Enable WAF (Web Application Firewall)
- Regular security updates
- Monitor for vulnerabilities:
  ```bash
  # Backend security scan
  cd apps/backend
  python -m safety check
  
  # Frontend security scan
  cd apps/frontend
  npm audit
  ```

### Database Security
```sql
-- PostgreSQL security settings
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET log_statement = 'mod';  -- Log modifications
SELECT pg_reload_conf();
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Database connectivity
curl http://localhost:8000/api/v1/health/db

# Full system status
curl http://localhost:8000/api/v1/status
```

### Backup Strategy
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump vessel_guard_prod > backups/db_backup_$DATE.sql

# File uploads backup
tar -czf backups/uploads_backup_$DATE.tar.gz uploads/

# Cleanup old backups (keep 7 days)
find backups/ -name "*.sql" -mtime +7 -delete
find backups/ -name "*.tar.gz" -mtime +7 -delete
```

### Monitoring Tools
- **Application**: Use built-in monitoring endpoints
- **Infrastructure**: Prometheus + Grafana
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Uptime**: UptimeRobot or similar

---

## 🎯 Next Steps

After completing the setup:

1. 📚 **Read the [User Guide](./docs/USER_GUIDE.md)** for detailed feature documentation
2. 🧪 **Run the test suite** to ensure everything works correctly
3. 🔧 **Customize** the configuration for your specific needs
4. 🚀 **Deploy** to your chosen environment
5. 📊 **Set up monitoring** and alerts

For additional help:
- 📖 [Complete Documentation](./docs/)
- 🐛 [Issue Tracker](https://github.com/ahmed-hesham07/Vessel-Guard/issues)
- 💬 [Discussions](https://github.com/ahmed-hesham07/Vessel-Guard/discussions)

Happy engineering! 🚀⚙️
