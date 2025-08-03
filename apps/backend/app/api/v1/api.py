"""
API v1 router for Vessel Guard API.

Aggregates all API endpoints and provides versioned routing.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    organizations,
    projects,
    vessels,
    materials,
    calculations,
    inspections,
    reports,
    status,
    tickets,
    monitoring,
    audit,
    bulk_operations,
)
from app.api.v1 import health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(status.router, tags=["status"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(vessels.router, prefix="/vessels", tags=["vessels"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(calculations.router, prefix="/calculations", tags=["calculations"])
api_router.include_router(inspections.router, prefix="/inspections", tags=["inspections"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(bulk_operations.router, prefix="/bulk", tags=["bulk-operations"])
