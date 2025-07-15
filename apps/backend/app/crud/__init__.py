"""
CRUD operations module.

Centralized import for all CRUD operations.
"""

from .base import CRUDBase
from .user import user_crud, CRUDUser
from .organization import organization, CRUDOrganization
from .project import project, CRUDProject
from .vessel import vessel, CRUDVessel
from .material import material, CRUDMaterial
from .calculation import calculation, CRUDCalculation
from .inspection import inspection, CRUDInspection
from .report import report, CRUDReport

__all__ = [
    "CRUDBase",
    "user_crud",
    "CRUDUser", 
    "organization",
    "CRUDOrganization",
    "project",
    "CRUDProject",
    "vessel",
    "CRUDVessel",
    "material",
    "CRUDMaterial",
    "calculation",
    "CRUDCalculation",
    "inspection",
    "CRUDInspection",
    "report",
    "CRUDReport"
]
