# Aiven Database Integration

This document describes the integration of Aiven PostgreSQL database with the Vessel Guard backend.

## Overview

The Vessel Guard backend has been updated to use Aiven PostgreSQL as the primary database. This provides a secure, managed PostgreSQL service with SSL encryption and automatic backups.

## Database Configuration

### Connection Details
- **Host**: `pg-f6419a9-vessel-guard.g.aivencloud.com`
- **Port**: `17500`
- **Database**: `defaultdb`
- **User**: `avnadmin`
- **SSL Mode**: `require`

### SSL Configuration
The connection uses SSL encryption with the provided CA certificate stored in `aiven-ca-cert.pem`.

## Environment Setup

### Production Environment (`.env`)
The production environment file is configured to use the Aiven database:
```bash
POSTGRES_SERVER=pg-f6419a9-vessel-guard.g.aivencloud.com
POSTGRES_USER=avnadmin
POSTGRES_PASSWORD=your_aiven_password_here
POSTGRES_DB=defaultdb
POSTGRES_PORT=17500
POSTGRES_SSL_MODE=require
POSTGRES_SSL_CERT_PATH=./aiven-ca-cert.pem
```

### Development Environment (`.env.development`)
For local development, you can still use a local PostgreSQL instance:
```bash
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=vessel_guard
POSTGRES_PORT=5432
POSTGRES_SSL_MODE=disable
```

## Files Modified

### Configuration Files
- `app/core/config.py` - Added SSL configuration support
- `app/db/base.py` - Updated to use new connection utilities
- `app/db/connection.py` - New connection management with SSL support
- `.env` - Updated with Aiven credentials
- `.env.development` - New development environment file

### Database Migration Setup
- `alembic.ini` - Alembic configuration for migrations
- `alembic/env.py` - Environment configuration for Alembic
- `alembic/script.py.mako` - Migration script template

### Utility Scripts
- `init_db.py` - Database initialization script
- `setup-aiven.ps1` - Setup script for Aiven integration

## Files Removed

All Fly.io related files have been completely removed from the project:
- ✅ `fly.toml` - Fly.io configuration (removed)
- ✅ `deploy-fly.ps1` - Fly.io deployment script (removed)
- ✅ `deploy-fly.sh` - Fly.io deployment bash script (removed)
- ✅ `FLY_DEPLOYMENT.md` - Fly.io deployment documentation (removed)
- ✅ `migrate_fly.py` - Fly.io migration script (removed)
- ✅ `requirements-fly.txt` - Fly.io requirements (removed)
- ✅ `.env.fly` - Fly.io environment file (removed)

The project now exclusively uses Aiven PostgreSQL for database services.

## Setup Instructions

### 1. Quick Setup
Run the setup script:
```powershell
.\setup-aiven.ps1 -Environment production -TestConnection
```

### 2. Manual Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the database:
   ```bash
   python init_db.py
   ```

3. Run migrations:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

4. Start the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Security Considerations

1. **SSL Encryption**: All connections to Aiven use SSL encryption
2. **Certificate Validation**: The CA certificate is used to validate the server
3. **Connection Limits**: Aiven has a connection limit of 20 concurrent connections
4. **Password Security**: Store the database password securely (consider using environment variables or Azure Key Vault)

## Connection Monitoring

The updated database connection includes:
- Connection pooling with pre-ping
- Automatic connection recycling
- SSL certificate verification
- Connection health checks
- Detailed logging

## Troubleshooting

### Common Issues

1. **SSL Certificate Error**
   - Ensure `aiven-ca-cert.pem` is in the correct location
   - Check that the certificate file is readable

2. **Connection Timeout**
   - Verify network connectivity to Aiven
   - Check that the host and port are correct

3. **Authentication Error**
   - Verify username and password
   - Check that the database name is correct

4. **Too Many Connections**
   - Aiven has a limit of 20 connections
   - Monitor connection pool usage
   - Consider implementing connection pooling

### Testing Connection

Use the initialization script to test the connection:
```bash
python init_db.py
```

This will test the connection and provide detailed information about the database.

## Migration from Local Database

If you have existing data in a local database:

1. Export your local data:
   ```bash
   pg_dump -h localhost -U postgres -d vessel_guard > backup.sql
   ```

2. Import to Aiven:
   ```bash
   psql -h pg-f6419a9-vessel-guard.g.aivencloud.com -U avnadmin -d defaultdb -p 17500 --set=sslmode=require < backup.sql
   ```

## Next Steps

1. **Configure Redis**: Set up Redis for caching and session management
2. **Email Configuration**: Configure SMTP settings for email notifications
3. **Update CORS**: Set proper CORS origins for your frontend domain
4. **Security**: Generate a secure SECRET_KEY for production
5. **Monitoring**: Set up monitoring and alerting for the database connection
