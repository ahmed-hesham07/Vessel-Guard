"""
CRUD operations for inspections.

Handles vessel inspection tracking including scheduling,
results recording, and compliance management.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.inspection import Inspection, InspectionStatus, InspectionResult
from app.db.models.vessel import Vessel
from app.db.models.project import Project
from app.schemas.inspection import InspectionCreate, InspectionUpdate


class CRUDInspection(CRUDBase[Inspection, InspectionCreate, InspectionUpdate]):
    """CRUD operations for inspections."""

    def get_by_vessel(
        self, db: Session, *, vessel_id: int, skip: int = 0, limit: int = 100
    ) -> List[Inspection]:
        """Get inspections for a vessel."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.vessel_id == vessel_id,
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.actual_completion_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_inspection_type(
        self, 
        db: Session, 
        *, 
        inspection_type: str,
        organization_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Inspection]:
        """Get inspections by type for organization."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.inspection_type == inspection_type,
                    Vessel.project.has(Project.organization_id == organization_id),
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.actual_completion_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Inspection]:
        """Get inspections for a project."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    self.model.vessel.has(project_id=project_id),
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.actual_completion_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_due_inspections(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        days_ahead: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inspection]:
        """Get inspections due in the next N days."""
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    Vessel.project.has(Project.organization_id == organization_id),
                    self.model.recommended_next_inspection.isnot(None),
                    self.model.recommended_next_inspection <= future_date,
                    self.model.recommended_next_inspection >= datetime.utcnow(),
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.recommended_next_inspection.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_overdue_inspections(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inspection]:
        """Get overdue inspections."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    Vessel.project.has(Project.organization_id == organization_id),
                    self.model.recommended_next_inspection.isnot(None),
                    self.model.recommended_next_inspection < datetime.utcnow(),
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.recommended_next_inspection.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_failed_inspections(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inspection]:
        """Get failed inspections for organization."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    Vessel.project.has(Project.organization_id == organization_id),
                    self.model.overall_result == InspectionResult.UNSAFE_FOR_OPERATION,
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.actual_completion_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent_inspections(
        self, 
        db: Session, 
        *, 
        organization_id: int, 
        days: int = 30,
        limit: int = 10
    ) -> List[Inspection]:
        """Get recent inspections for organization."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    Vessel.project.has(Project.organization_id == organization_id),
                    self.model.actual_completion_date >= cutoff_date,
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.actual_completion_date.desc())
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
    ) -> List[Inspection]:
        """Search inspections by inspector name, inspection type, or findings."""
        search_term = f"%{query.lower()}%"
        
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    Vessel.project.has(Project.organization_id == organization_id),
                    or_(
                        func.lower(self.model.inspector_notes).contains(search_term),
                        func.lower(self.model.inspection_type).contains(search_term),
                        func.lower(self.model.recommendations).contains(search_term)
                    ),
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.actual_completion_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_inspection_statistics(
        self, db: Session, *, organization_id: int
    ) -> Dict[str, Any]:
        """Get inspection statistics for organization."""
        base_query = (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    Vessel.project.has(Project.organization_id == organization_id),
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
        )

        total_inspections = base_query.count()
        
        passed_inspections = base_query.filter(
            self.model.overall_result == InspectionResult.SATISFACTORY
        ).count()
        
        failed_inspections = base_query.filter(
            self.model.overall_result == InspectionResult.UNSAFE_FOR_OPERATION
        ).count()
        
        # Get overdue inspections count
        overdue_inspections = (
            base_query
            .filter(
                and_(
                    self.model.recommended_next_inspection.isnot(None),
                    self.model.recommended_next_inspection < datetime.utcnow()
                )
            )
            .count()
        )
        
        # Get due soon inspections count
        future_date = datetime.utcnow() + timedelta(days=30)
        due_soon_inspections = (
            base_query
            .filter(
                and_(
                    self.model.recommended_next_inspection.isnot(None),
                    self.model.recommended_next_inspection <= future_date,
                    self.model.recommended_next_inspection >= datetime.utcnow()
                )
            )
            .count()
        )

        # Calculate by type
        type_stats = (
            base_query
            .with_entities(
                self.model.inspection_type,
                func.count(self.model.id).label('count')
            )
            .group_by(self.model.inspection_type)
            .all()
        )
        
        inspections_by_type = {stat[0]: stat[1] for stat in type_stats}
        
        # Calculate pass rate
        pass_rate = (
            (passed_inspections / total_inspections * 100) 
            if total_inspections > 0 else 0
        )

        return {
            "total_inspections": total_inspections,
            "passed_inspections": passed_inspections,
            "failed_inspections": failed_inspections,
            "overdue_inspections": overdue_inspections,
            "due_soon_inspections": due_soon_inspections,
            "inspections_by_type": inspections_by_type,
            "pass_rate": round(pass_rate, 2)
        }

    def schedule_next_inspection(
        self, 
        db: Session, 
        *, 
        inspection_id: int, 
        recommended_next_inspection: datetime,
        interval_months: Optional[int] = None
    ) -> Optional[Inspection]:
        """Schedule next inspection."""
        inspection = self.get(db, id=inspection_id)
        if inspection:
            update_data = {
                "recommended_next_inspection": recommended_next_inspection,
                "inspection_interval_months": interval_months
            }
            return self.update(db, db_obj=inspection, obj_in=update_data)
        return None

    def get_inspection_count_by_vessel(
        self, db: Session, *, vessel_id: int
    ) -> int:
        """Get count of inspections for a vessel."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.vessel_id == vessel_id,
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .count()
        )

    def get_inspection_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """Get count of inspections for organization."""
        return (
            db.query(self.model)
            .join(self.model.vessel)
            .filter(
                and_(
                    Vessel.project.has(Project.organization_id == organization_id),
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .count()
        )

    def get_latest_inspection_by_vessel(
        self, db: Session, *, vessel_id: int
    ) -> Optional[Inspection]:
        """Get the latest inspection for a vessel."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.vessel_id == vessel_id,
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.actual_completion_date.desc())
            .first()
        )

    def get_inspection_history(
        self, 
        db: Session, 
        *, 
        vessel_id: int,
        years: int = 5
    ) -> List[Inspection]:
        """Get inspection history for a vessel."""
        cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
        
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.vessel_id == vessel_id,
                    self.model.actual_completion_date >= cutoff_date,
                    self.model.status != InspectionStatus.CANCELLED
                )
            )
            .order_by(self.model.actual_completion_date.desc())
            .all()
        )


inspection = CRUDInspection(Inspection)
