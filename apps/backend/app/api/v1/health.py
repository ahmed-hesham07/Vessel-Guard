"""
Health check endpoints for monitoring application status.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis
import psutil
import time
from datetime import datetime

from app.db.base import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns 200 if the service is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "vessel-guard-api",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with dependency status.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "vessel-guard-api",
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check database connection
    try:
        start_time = time.time()
        db.execute(text("SELECT 1"))
        db_response_time = time.time() - start_time
        health_status["dependencies"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(db_response_time * 1000, 2)
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["dependencies"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Redis connection (if configured)
    if settings.REDIS_URL:
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            start_time = time.time()
            redis_client.ping()
            redis_response_time = time.time() - start_time
            health_status["dependencies"]["redis"] = {
                "status": "healthy",
                "response_time_ms": round(redis_response_time * 1000, 2)
            }
        except Exception as e:
            health_status["dependencies"]["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
    else:
        health_status["dependencies"]["redis"] = {
            "status": "not_configured"
        }
    
    return health_status


@router.get("/health/system")
async def system_health_check() -> Dict[str, Any]:
    """
    System resource health check.
    """
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Determine health status based on thresholds
    status = "healthy"
    if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
        status = "degraded"
    if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
        status = "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu": {
                "usage_percent": cpu_percent,
                "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 90 else "critical"
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent,
                "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 90 else "critical"
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": disk.percent,
                "status": "healthy" if disk.percent < 80 else "warning" if disk.percent < 90 else "critical"
            }
        }
    }


@router.get("/health/readiness")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness check for Kubernetes/container orchestration.
    Returns 200 only if the service is ready to accept traffic.
    """
    checks = []
    all_ready = True
    
    # Database readiness
    try:
        db.execute(text("SELECT 1"))
        checks.append({"name": "database", "status": "ready"})
    except Exception as e:
        all_ready = False
        checks.append({"name": "database", "status": "not_ready", "error": str(e)})
    
    # Redis readiness (if configured)
    if settings.REDIS_URL:
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            checks.append({"name": "redis", "status": "ready"})
        except Exception as e:
            all_ready = False
            checks.append({"name": "redis", "status": "not_ready", "error": str(e)})
    
    if not all_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@router.get("/health/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes/container orchestration.
    Returns 200 if the service is alive (should restart if this fails).
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "vessel-guard-api"
    }
