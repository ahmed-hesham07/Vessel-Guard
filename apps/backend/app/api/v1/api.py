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
)

api_router = APIRouter()

# Include all endpoint routers
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
