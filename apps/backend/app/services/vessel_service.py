"""
Vessel service layer for handling vessel-related business logic.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.models.vessel import Vessel
from app.schemas.vessel import VesselCreate, VesselUpdate
from app.core.exceptions import ValidationError, NotFoundError


class VesselService:
    """Service class for vessel operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_vessel(self, vessel_data: VesselCreate, project_id: int,
                     organization_id: int, created_by_id: int) -> Vessel:
        """Create a new vessel."""
        # Validate design pressure
        if vessel_data.design_pressure <= 0:
            raise ValidationError("Design pressure must be positive")
        
        db_vessel = Vessel(
            **vessel_data.dict(),
            project_id=project_id,
            organization_id=organization_id,
            created_by_id=created_by_id,
            is_active=True
        )
        
        self.db.add(db_vessel)
        self.db.commit()
        self.db.refresh(db_vessel)
        return db_vessel
    
    def get_vessel_by_id(self, vessel_id: int) -> Optional[Vessel]:
        """Get vessel by ID."""
        return self.db.query(Vessel).filter(Vessel.id == vessel_id).first()
    
    def update_vessel(self, vessel_id: int, vessel_data: VesselUpdate) -> Vessel:
        """Update vessel."""
        vessel = self.get_vessel_by_id(vessel_id)
        if not vessel:
            raise NotFoundError("Vessel not found")
        
        update_data = vessel_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vessel, field, value)
        
        self.db.commit()
        self.db.refresh(vessel)
        return vessel
    
    def get_project_vessels(self, project_id: int) -> List[Vessel]:
        """Get all vessels for a project."""
        return self.db.query(Vessel).filter(
            Vessel.project_id == project_id
        ).all()
