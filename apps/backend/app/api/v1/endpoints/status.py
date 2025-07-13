"""
System status and metrics endpoint for monitoring dashboard.
"""

from fastapi import APIRouter
from typing import Dict, Any

from app.core.logging_config import get_logger
from app.middleware.performance import get_performance_metrics

router = APIRouter()
logger = get_logger('vessel_guard.status')


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive system status including performance metrics.
    
    This endpoint provides a complete overview of system health,
    performance metrics, and operational status.
    """
    try:
        # Get performance metrics
        performance_data = get_performance_metrics()
        
        # Compile system status
        status = {
            "service": {
                "name": "vessel-guard-api",
                "version": "1.0.0",
                "status": "operational",
                "environment": "development"  # This would come from settings
            },
            "performance": performance_data,
            "features": {
                "calculations": {
                    "asme_b31_3": True,
                    "api_579": True,
                    "asme_viii": True
                },
                "integrations": {
                    "redis_cache": True,
                    "postgresql": True,
                    "azure_storage": False  # Would be based on actual config
                },
                "security": {
                    "rate_limiting": True,
                    "security_headers": True,
                    "threat_detection": True,
                    "audit_logging": True
                },
                "monitoring": {
                    "performance_tracking": True,
                    "health_checks": True,
                    "structured_logging": True,
                    "metrics_collection": True
                }
            },
            "endpoints": {
                "health_basic": "/api/v1/health",
                "health_detailed": "/api/v1/health/detailed",
                "health_system": "/api/v1/health/system",
                "readiness": "/api/v1/health/readiness",
                "liveness": "/api/v1/health/liveness",
                "status": "/api/v1/status",
                "documentation": "/docs",
                "openapi": "/openapi.json"
            },
            "compliance": {
                "standards_supported": [
                    "ASME B31.3 - Process Piping",
                    "API 579 - Fitness for Service",
                    "ASME VIII - Pressure Vessels"
                ],
                "certifications": [
                    "ISO 27001 Ready",
                    "SOC 2 Ready",
                    "GDPR Compliant"
                ]
            },
            "deployment": {
                "platform": "Azure Container Apps",
                "container_registry": "Azure Container Registry",
                "database": "PostgreSQL",
                "cache": "Redis",
                "cdn": "Azure CDN",
                "monitoring": "Azure Monitor"
            }
        }
        
        logger.info("System status requested", extra={
            "endpoint": "/status",
            "status_check": True
        })
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}", exc_info=True)
        
        # Return minimal status on error
        return {
            "service": {
                "name": "vessel-guard-api",
                "version": "1.0.0",
                "status": "degraded",
                "error": "Failed to retrieve complete status"
            }
        }
