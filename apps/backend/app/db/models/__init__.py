"""
Database models for the Vessel Guard application.

This module imports all database models to make them available
for SQLAlchemy metadata creation and Alembic migrations.
"""

from app.db.models.user import User
from app.db.models.organization import Organization
from app.db.models.project import Project
from app.db.models.vessel import Vessel
from app.db.models.material import Material
from app.db.models.calculation import Calculation, CalculationResult
from app.db.models.inspection import Inspection
from app.db.models.report import Report
from app.db.models.ticket import Ticket
from app.core.audit import AuditLog
from app.core.session_manager import UserSession

__all__ = [
    "User",
    "Organization", 
    "Project",
    "Vessel",
    "Material",
    "Calculation",
    "CalculationResult",
    "Inspection",
    "Report",
    "Ticket",
    "AuditLog",
    "UserSession"
]
