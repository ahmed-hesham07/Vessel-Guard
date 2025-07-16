# Fly.io Deployment Guide for Vessel Guard Backend

This guide covers deploying the Vessel Guard backend API to Fly.io with PostgreSQL database integration.

## Prerequisites

1. **Install Fly.io CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up and authenticate**
   ```bash
   flyctl auth signup
   flyctl auth login
   ```

## Database Setup

### 1. Create PostgreSQL Database
```bash
flyctl postgres create --name vessel-guard-db --region sea --vm-size shared-cpu-1x --volume-size 3
```

### 2. Attach Database to App
```bash
flyctl postgres attach vessel-guard-db --app vessel-guard-backend
```

This will automatically set the `DATABASE_URL` secret in your app.

## Environment Variables

### Required Secrets
Set these secrets using `flyctl secrets set`:

```bash
# Security
flyctl secrets set SECRET_KEY=your-super-secret-key-here

# Database (if not using attached PostgreSQL)
flyctl secrets set POSTGRES_PASSWORD=your-postgres-password

# Email (optional)
flyctl secrets set SMTP_PASSWORD=your-smtp-password
flyctl secrets set SMTP_USER=your-smtp-user

# Frontend URL
flyctl secrets set FRONTEND_URL=https://your-frontend-domain.com
```

### Environment Configuration
The app uses `.env.fly` for non-sensitive configuration. Update this file with your settings:

- `POSTGRES_SERVER`: Database hostname (usually `vessel-guard-db.flycast`)
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins
- `SMTP_HOST`: Email server hostname
- `FROM_EMAIL`: Email sender address

## Deployment

### Automated Deployment
Use the provided deployment script:

```bash
# Windows
.\deploy-fly.ps1

# macOS/Linux
./deploy-fly.sh
```

### Manual Deployment

1. **Create the app** (if not exists):
   ```bash
   flyctl apps create vessel-guard-backend
   ```

2. **Deploy**:
   ```bash
   flyctl deploy
   ```

## Configuration Files

### fly.toml
Main Fly.io configuration file with:
- App name and region settings
- Port and health check configuration
- Deployment strategy
- Release command for database migrations

### Dockerfile
Optimized for Fly.io deployment:
- Uses Python 3.11 Alpine for smaller image size
- Installs only production dependencies
- Includes health check endpoint
- Proper signal handling for graceful shutdown

### .dockerignore
Excludes development files and reduces build context size.

## Database Migration

The app includes an automated migration script (`migrate_fly.py`) that:
1. Tests database connectivity
2. Runs Alembic migrations (if available)
3. Falls back to database initialization if needed

## Monitoring and Logs

### View Logs
```bash
flyctl logs --app vessel-guard-backend
```

### Monitor App Status
```bash
flyctl status --app vessel-guard-backend
```

### Health Check
The app includes a comprehensive health check at `/health` that monitors:
- API status
- Database connectivity
- Environment information

## Scaling

### Scale Instances
```bash
flyctl scale count 2 --app vessel-guard-backend
```

### Scale VM Size
```bash
flyctl scale vm shared-cpu-2x --app vessel-guard-backend
```

## Troubleshooting

### Database Connection Issues
1. Check if database is running:
   ```bash
   flyctl postgres list
   ```

2. Verify database attachment:
   ```bash
   flyctl postgres show vessel-guard-db
   ```

3. Check app secrets:
   ```bash
   flyctl secrets list --app vessel-guard-backend
   ```

### Application Errors
1. Check logs:
   ```bash
   flyctl logs --app vessel-guard-backend
   ```

2. SSH into the app:
   ```bash
   flyctl ssh console --app vessel-guard-backend
   ```

### Performance Issues
1. Monitor metrics:
   ```bash
   flyctl dashboard --app vessel-guard-backend
   ```

2. Check resource usage:
   ```bash
   flyctl status --app vessel-guard-backend
   ```

## Security Considerations

1. **Secrets Management**: Never commit secrets to version control
2. **CORS Configuration**: Restrict CORS origins to your frontend domain
3. **Database Security**: Use strong passwords and enable SSL
4. **API Keys**: Rotate API keys regularly
5. **Updates**: Keep dependencies updated

## Cost Optimization

1. **Instance Sizing**: Start with `shared-cpu-1x` and scale as needed
2. **Database Size**: Monitor storage usage and adjust volume size
3. **Region Selection**: Choose region closest to your users
4. **Auto-scaling**: Configure auto-scaling based on metrics

## Backup and Recovery

### Database Backups
```bash
flyctl postgres backup create --app vessel-guard-db
```

### Application Rollback
```bash
flyctl releases --app vessel-guard-backend
flyctl releases rollback <release-id> --app vessel-guard-backend
```

## Next Steps

1. Set up CI/CD pipeline for automated deployments
2. Configure custom domain
3. Set up monitoring and alerting
4. Implement log aggregation
5. Configure SSL certificates
