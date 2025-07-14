"""
CRUD operations for calculations.

Handles pressure vessel engineering calculations including
ASME calculations, stress analysis, and design verification.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationUpdate


class CRUDCalculation(CRUDBase[Calculation, CalculationCreate, CalculationUpdate]):
    """CRUD operations for calculations."""

    def get_by_vessel(
        self, db: Session, *, vessel_id: int, skip: int = 0, limit: int = 100
    ) -> List[Calculation]:
        """Get calculations for a vessel."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.vessel_id == vessel_id,
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_calculation_type(
        self, 
        db: Session, 
        *, 
        calculation_type: str,
        organization_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Calculation]:
        """Get calculations by type for organization."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.calculation_type == calculation_type,
                    self.model.vessel.has(organization_id=organization_id),
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Calculation]:
        """Get calculations for a project."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.vessel.has(project_id=project_id),
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent_calculations(
        self, 
        db: Session, 
        *, 
        organization_id: int, 
        days: int = 30,
        limit: int = 10
    ) -> List[Calculation]:
        """Get recent calculations for organization."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.vessel.has(organization_id=organization_id),
                    self.model.created_at >= cutoff_date,
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_failed_calculations(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Calculation]:
        """Get failed calculations for organization."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.vessel.has(organization_id=organization_id),
                    self.model.status == "failed",
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_calculations_needing_review(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Calculation]:
        """Get calculations that need engineering review."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.vessel.has(organization_id=organization_id),
                    self.model.status == "completed",
                    self.model.reviewed_by_id.is_(None),
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self, 
        db: Session, 
        *, 
        query: str, 
        organization_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Calculation]:
        """Search calculations by name, description, or calculation type."""
        search_term = f"%{query.lower()}%"
        
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.vessel.has(organization_id=organization_id),
                    or_(
                        func.lower(self.model.name).contains(search_term),
                        func.lower(self.model.description).contains(search_term),
                        func.lower(self.model.calculation_type).contains(search_term)
                    ),
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_calculation_statistics(
        self, db: Session, *, organization_id: int
    ) -> Dict[str, Any]:
        """Get calculation statistics for organization."""
        base_query = (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.vessel.has(organization_id=organization_id),
                    self.model.is_active == True
                )
            )
        )

        total_calculations = base_query.count()
        
        completed_calculations = base_query.filter(
            self.model.status == "completed"
        ).count()
        
        failed_calculations = base_query.filter(
            self.model.status == "failed"
        ).count()
        
        pending_calculations = base_query.filter(
            self.model.status == "pending"
        ).count()
        
        calculations_needing_review = base_query.filter(
            and_(
                self.model.status == "completed",
                self.model.reviewed_by_id.is_(None)
            )
        ).count()

        # Calculate by type
        type_stats = (
            base_query
            .with_entities(
                self.model.calculation_type,
                func.count(self.model.id).label('count')
            )
            .group_by(self.model.calculation_type)
            .all()
        )
        
        calculations_by_type = {stat[0]: stat[1] for stat in type_stats}
        
        # Calculate success rate
        success_rate = (
            (completed_calculations / total_calculations * 100) 
            if total_calculations > 0 else 0
        )

        return {
            "total_calculations": total_calculations,
            "completed_calculations": completed_calculations,
            "failed_calculations": failed_calculations,
            "pending_calculations": pending_calculations,
            "calculations_needing_review": calculations_needing_review,
            "calculations_by_type": calculations_by_type,
            "success_rate": round(success_rate, 2)
        }

    def mark_as_reviewed(
        self, 
        db: Session, 
        *, 
        calculation_id: int, 
        reviewed_by_id: int,
        review_notes: Optional[str] = None
    ) -> Optional[Calculation]:
        """Mark calculation as reviewed."""
        calculation = self.get(db, id=calculation_id)
        if calculation:
            update_data = {
                "reviewed_by_id": reviewed_by_id,
                "reviewed_at": datetime.utcnow(),
                "review_notes": review_notes
            }
            return self.update(db, db_obj=calculation, obj_in=update_data)
        return None

    def update_status(
        self, 
        db: Session, 
        *, 
        calculation_id: int, 
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[Calculation]:
        """Update calculation status."""
        calculation = self.get(db, id=calculation_id)
        if calculation:
            update_data = {
                "status": status,
                "completed_at": datetime.utcnow() if status == "completed" else None,
                "error_message": error_message
            }
            return self.update(db, db_obj=calculation, obj_in=update_data)
        return None

    def get_calculation_count_by_vessel(
        self, db: Session, *, vessel_id: int
    ) -> int:
        """Get count of calculations for a vessel."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.vessel_id == vessel_id,
                    self.model.is_active == True
                )
            )
            .count()
        )

    def get_calculation_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """Get count of calculations for organization."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.vessel.has(organization_id=organization_id),
                    self.model.is_active == True
                )
            )
            .count()
        )


calculation = CRUDCalculation(Calculation)
