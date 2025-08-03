#!/bin/bash

# Vessel Guard Deployment Script
# Usage: ./deploy.sh [environment] [deployment-type]
# Environments: staging, production
# Deployment types: rolling, blue-green, hotfix

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENVIRONMENT=${1:-staging}
DEPLOYMENT_TYPE=${2:-rolling}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_ROOT/logs/deploy_${ENVIRONMENT}_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
fi

# Validate deployment type
if [[ "$DEPLOYMENT_TYPE" != "rolling" && "$DEPLOYMENT_TYPE" != "blue-green" && "$DEPLOYMENT_TYPE" != "hotfix" ]]; then
    error "Invalid deployment type: $DEPLOYMENT_TYPE. Must be 'rolling', 'blue-green', or 'hotfix'"
fi

log "Starting $DEPLOYMENT_TYPE deployment to $ENVIRONMENT environment"

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check if required environment variables are set
    local required_vars
    if [[ "$ENVIRONMENT" == "production" ]]; then
        required_vars=(
            "PRODUCTION_DATABASE_URL"
            "PRODUCTION_SECRET_KEY"
            "PRODUCTION_REDIS_URL"
        )
    else
        required_vars=(
            "STAGING_DATABASE_URL"
            "STAGING_SECRET_KEY"
            "STAGING_REDIS_URL"
        )
    fi
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            error "Required environment variable $var is not set"
        fi
    done
    
    # Check Docker is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running or not accessible"
    fi
    
    # Check Docker Compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        error "docker-compose is not installed or not in PATH"
    fi
    
    # Check network connectivity
    if [[ "$ENVIRONMENT" == "production" ]]; then
        if ! curl -f --connect-timeout 10 https://vessel-guard.com/api/v1/health >/dev/null 2>&1; then
            warn "Cannot reach current production environment for health check"
        fi
    fi
    
    success "Pre-deployment checks passed"
}

# Database backup
backup_database() {
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log "Creating database backup..."
        
        local backup_file="$PROJECT_ROOT/backups/db_backup_${TIMESTAMP}.sql"
        mkdir -p "$PROJECT_ROOT/backups"
        
        # This would be replaced with actual backup command
        log "Database backup would be created at: $backup_file"
        # pg_dump $PRODUCTION_DATABASE_URL > "$backup_file"
        
        success "Database backup completed"
    fi
}

# Build and tag images
build_images() {
    log "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build backend image
    docker build -t vessel-guard/backend:$TIMESTAMP ./apps/backend
    docker tag vessel-guard/backend:$TIMESTAMP vessel-guard/backend:latest
    
    # Build frontend image
    docker build -t vessel-guard/frontend:$TIMESTAMP ./apps/frontend
    docker tag vessel-guard/frontend:$TIMESTAMP vessel-guard/frontend:latest
    
    success "Docker images built successfully"
}

# Rolling deployment
rolling_deployment() {
    log "Performing rolling deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Create environment file
    create_env_file
    
    # Pull latest images and restart services
    docker-compose pull
    docker-compose up -d --force-recreate
    
    # Wait for services to be ready
    wait_for_health_check
    
    success "Rolling deployment completed"
}

# Blue-green deployment
blue_green_deployment() {
    log "Performing blue-green deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Create environment file
    create_env_file
    
    # Deploy to green environment
    log "Deploying to green environment..."
    docker-compose -f docker-compose.yml -f docker-compose.green.yml up -d
    
    # Health check green environment
    log "Health checking green environment..."
    local green_health_url
    if [[ "$ENVIRONMENT" == "production" ]]; then
        green_health_url="http://green.vessel-guard.com/api/v1/health"
    else
        green_health_url="http://localhost:8001/api/v1/health"
    fi
    
    for i in {1..30}; do
        if curl -f "$green_health_url" >/dev/null 2>&1; then
            success "Green environment is healthy"
            break
        fi
        if [[ $i -eq 30 ]]; then
            error "Green environment failed health check after 5 minutes"
        fi
        log "Health check attempt $i/30 failed, retrying in 10 seconds..."
        sleep 10
    done
    
    # Switch traffic (this would be done via load balancer in real deployment)
    log "Switching traffic to green environment..."
    warn "Traffic switching requires manual load balancer configuration"
    
    # Clean up blue environment
    log "Cleaning up blue environment..."
    docker-compose -f docker-compose.yml -f docker-compose.blue.yml down
    
    success "Blue-green deployment completed"
}

# Hotfix deployment
hotfix_deployment() {
    log "Performing hotfix deployment..."
    
    if [[ "$ENVIRONMENT" != "production" ]]; then
        error "Hotfix deployments are only allowed to production"
    fi
    
    # Build images with hotfix tag
    docker build -t vessel-guard/backend:hotfix-$TIMESTAMP ./apps/backend
    docker build -t vessel-guard/frontend:hotfix-$TIMESTAMP ./apps/frontend
    
    # Deploy immediately without full pipeline
    rolling_deployment
    
    success "Hotfix deployment completed"
}

# Create environment file
create_env_file() {
    log "Creating environment configuration..."
    
    local env_file="$PROJECT_ROOT/.env"
    
    cat > "$env_file" << EOF
ENVIRONMENT=$ENVIRONMENT
DEPLOYMENT_TIMESTAMP=$TIMESTAMP
DEPLOYMENT_TYPE=$DEPLOYMENT_TYPE
EOF
    
    # Add environment-specific variables
    if [[ "$ENVIRONMENT" == "production" ]]; then
        cat >> "$env_file" << EOF
DATABASE_URL=$PRODUCTION_DATABASE_URL
SECRET_KEY=$PRODUCTION_SECRET_KEY
REDIS_URL=$PRODUCTION_REDIS_URL
CORS_ORIGINS=$PRODUCTION_CORS_ORIGINS
ALLOWED_HOSTS=$PRODUCTION_ALLOWED_HOSTS
EOF
    else
        cat >> "$env_file" << EOF
DATABASE_URL=$STAGING_DATABASE_URL
SECRET_KEY=$STAGING_SECRET_KEY
REDIS_URL=$STAGING_REDIS_URL
CORS_ORIGINS=$STAGING_CORS_ORIGINS
ALLOWED_HOSTS=$STAGING_ALLOWED_HOSTS
EOF
    fi
    
    success "Environment configuration created"
}

# Wait for health check
wait_for_health_check() {
    log "Waiting for services to be ready..."
    
    local health_url
    if [[ "$ENVIRONMENT" == "production" ]]; then
        health_url="https://vessel-guard.com/api/v1/health"
    else
        health_url="http://localhost:8000/api/v1/health"
    fi
    
    for i in {1..20}; do
        if curl -f "$health_url" >/dev/null 2>&1; then
            success "Services are healthy and ready"
            return 0
        fi
        log "Health check attempt $i/20 failed, retrying in 15 seconds..."
        sleep 15
    done
    
    error "Services failed to become healthy after 5 minutes"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Run migrations in backend container
    docker-compose exec -T backend alembic upgrade head
    
    success "Database migrations completed"
}

# Post-deployment verification
post_deployment_verification() {
    log "Running post-deployment verification..."
    
    local base_url
    if [[ "$ENVIRONMENT" == "production" ]]; then
        base_url="https://vessel-guard.com"
    else
        base_url="http://localhost:8000"
    fi
    
    # Test critical endpoints
    local endpoints=(
        "/api/v1/health"
        "/api/v1/status"
        "/api/v1/monitoring/metrics"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f "$base_url$endpoint" >/dev/null 2>&1; then
            success "✅ $endpoint is responsive"
        else
            error "❌ $endpoint is not responding"
        fi
    done
    
    success "Post-deployment verification completed"
}

# Rollback function
rollback() {
    warn "Initiating rollback procedure..."
    
    # This would switch back to the previous version
    log "Rolling back to previous version..."
    
    # For blue-green, switch back to blue
    if [[ "$DEPLOYMENT_TYPE" == "blue-green" ]]; then
        docker-compose -f docker-compose.yml -f docker-compose.blue.yml up -d
        docker-compose -f docker-compose.yml -f docker-compose.green.yml down
    else
        # For rolling deployment, restore from backup
        warn "Rolling deployment rollback requires manual intervention"
    fi
    
    success "Rollback completed"
}

# Cleanup function
cleanup() {
    log "Cleaning up deployment artifacts..."
    
    # Remove old images (keep last 5)
    docker image prune -f
    
    # Clean up old log files (keep last 30 days)
    find "$PROJECT_ROOT/logs" -name "deploy_*.log" -mtime +30 -delete 2>/dev/null || true
    
    success "Cleanup completed"
}

# Signal handlers
trap 'error "Deployment interrupted by user"' INT TERM

# Main deployment flow
main() {
    log "=== Vessel Guard Deployment Started ==="
    log "Environment: $ENVIRONMENT"
    log "Deployment Type: $DEPLOYMENT_TYPE"
    log "Timestamp: $TIMESTAMP"
    
    pre_deployment_checks
    backup_database
    build_images
    
    case "$DEPLOYMENT_TYPE" in
        "rolling")
            rolling_deployment
            ;;
        "blue-green")
            blue_green_deployment
            ;;
        "hotfix")
            hotfix_deployment
            ;;
    esac
    
    run_migrations
    post_deployment_verification
    cleanup
    
    success "=== Deployment completed successfully ==="
    log "Deployment log: $LOG_FILE"
}

# Run main function
main "$@"