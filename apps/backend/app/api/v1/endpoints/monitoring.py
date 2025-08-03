"""
Monitoring and health check endpoints.

Provides comprehensive system monitoring, health checks,
and metrics collection for operational visibility.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, require_role
from app.db.models.user import User, UserRole
from app.services.monitoring_service import (
    metrics_collector,
    health_checker,
    alert_manager,
    collect_all_metrics
)
from app.services.optimization_service import (
    query_optimizer,
    db_monitor
)
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint.
    
    Returns basic application health status without authentication.
    Used by load balancers and monitoring systems.
    """
    try:
        health_status = health_checker.check_application_health()
        
        # Return appropriate HTTP status based on health
        if health_status['overall_status'] == 'unhealthy':
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
        elif health_status['overall_status'] == 'degraded':
            # Still return 200 but with degraded status
            logger.warning(f"System health is degraded: {health_status.get('details', {})}")
            # Add degraded status to response headers for monitoring
            response.headers["X-Health-Status"] = "degraded"
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "overall_status": "unhealthy",
                "error": str(e),
                "message": "Health check failed"
            }
        )


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Detailed health check with comprehensive system status.
    
    Requires authentication and engineer role.
    """
    try:
        health_status = health_checker.check_application_health()
        
        # Add additional detailed information
        health_status['details'] = {
            'user_id': current_user.id,
            'organization_id': current_user.organization_id,
            'check_timestamp': health_status['timestamp']
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detailed health check failed: {str(e)}"
        )


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics(
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Get comprehensive application metrics.
    
    Returns system, application, and database metrics.
    Requires engineer role for access.
    """
    try:
        metrics = collect_all_metrics()
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics collection failed: {str(e)}"
        )


@router.get("/metrics/system", response_model=Dict[str, Any])
async def get_system_metrics(
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get system-level metrics only."""
    try:
        system_metrics = metrics_collector.collect_system_metrics()
        return system_metrics.to_dict()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System metrics collection failed: {str(e)}"
        )


@router.get("/metrics/application", response_model=Dict[str, Any])
async def get_application_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get application-level metrics only."""
    try:
        app_metrics = metrics_collector.collect_application_metrics(db)
        return app_metrics.to_dict()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Application metrics collection failed: {str(e)}"
        )


@router.get("/metrics/database", response_model=Dict[str, Any])
async def get_database_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get database-level metrics only."""
    try:
        db_metrics = metrics_collector.collect_database_metrics(db)
        return db_metrics.to_dict()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database metrics collection failed: {str(e)}"
        )


@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats(
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get cache system statistics."""
    try:
        # Test cache operations and get basic stats
        stats = {
            "cache_enabled": cache_service.enabled,
            "redis_available": cache_service.redis_client is not None
        }
        
        if cache_service.enabled and cache_service.redis_client:
            try:
                # Get Redis info
                info = cache_service.redis_client.info()
                stats.update({
                    "redis_version": info.get('redis_version'),
                    "used_memory": info.get('used_memory'),
                    "used_memory_human": info.get('used_memory_human'),
                    "connected_clients": info.get('connected_clients'),
                    "total_commands_processed": info.get('total_commands_processed'),
                    "keyspace_hits": info.get('keyspace_hits', 0),
                    "keyspace_misses": info.get('keyspace_misses', 0)
                })
                
                # Calculate hit rate
                hits = stats.get('keyspace_hits', 0)
                misses = stats.get('keyspace_misses', 0)
                total_requests = hits + misses
                
                if total_requests > 0:
                    stats['hit_rate'] = (hits / total_requests) * 100
                else:
                    stats['hit_rate'] = 0.0
                    
            except Exception as e:
                stats['redis_error'] = str(e)
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache stats collection failed: {str(e)}"
        )


@router.post("/cache/clear", response_model=Dict[str, Any])
async def clear_cache(
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Clear application cache."""
    try:
        if cache_service.enabled:
            success = cache_service.flush_all()
            return {
                "success": success,
                "message": "Cache cleared successfully" if success else "Cache clear failed"
            }
        else:
            return {
                "success": False,
                "message": "Cache service is not enabled"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache clear failed: {str(e)}"
        )


@router.get("/database/connections", response_model=Dict[str, Any])
async def get_database_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get database connection statistics."""
    try:
        connection_stats = db_monitor.get_connection_stats(db)
        return connection_stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection stats failed: {str(e)}"
        )


@router.get("/database/sizes", response_model=List[Dict[str, Any]])
async def get_database_sizes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get database table sizes."""
    try:
        table_sizes = db_monitor.get_table_sizes(db)
        return table_sizes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database size stats failed: {str(e)}"
        )


@router.get("/database/slow-queries", response_model=List[Dict[str, Any]])
async def get_slow_queries(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get slow database queries."""
    try:
        slow_queries = query_optimizer.get_slow_queries(db, limit=limit)
        return slow_queries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Slow queries retrieval failed: {str(e)}"
        )


@router.post("/database/explain", response_model=Dict[str, Any])
async def explain_query(
    query_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """
    Explain a database query for performance analysis.
    
    Request body should contain: {"query": "SELECT * FROM table_name"}
    """
    try:
        if "query" not in query_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query parameter is required"
            )
        
        query = query_data["query"]
        
        # Basic SQL injection protection
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
        query_upper = query.upper()
        
        if any(keyword in query_upper for keyword in dangerous_keywords):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only SELECT queries are allowed for explanation"
            )
        
        explanation = query_optimizer.explain_query(db, query)
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query explanation failed: {str(e)}"
        )


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_recent_alerts(
    current_user: User = Depends(require_role([UserRole.ENGINEER]))
):
    """Get recent alerts from the system."""
    try:
        # Get recent alerts from cache
        alert_keys = []
        if cache_service.enabled and cache_service.redis_client:
            try:
                alert_keys = cache_service.redis_client.keys("vessel_guard:alert:*")
            except Exception as e:
                logger.warning(f"Failed to fetch alert keys from Redis: {e}")
                # Continue with empty list to gracefully handle Redis failures
                alert_keys = []
        
        alerts = []
        for key in alert_keys[-20:]:  # Get last 20 alerts
            try:
                alert_data = cache_service.get(key.decode() if isinstance(key, bytes) else key)
                if alert_data:
                    alerts.append(alert_data)
            except Exception:
                continue
        
        # Sort by timestamp if available
        alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return alerts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert retrieval failed: {str(e)}"
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_system_status():
    """
    Get overall system status for external monitoring.
    
    Returns simplified status without authentication.
    """
    try:
        health_status = health_checker.check_application_health()
        
        return {
            "status": health_status['overall_status'],
            "timestamp": health_status['timestamp'],
            "version": "1.0.0",
            "service": "vessel-guard-api"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": None,
            "version": "1.0.0",
            "service": "vessel-guard-api"
        }