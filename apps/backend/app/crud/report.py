"""
CRUD operations for reports.

Handles report generation, storage, and retrieval for
vessels, calculations, and inspections.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate


class CRUDReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    """CRUD operations for reports."""

    def get_by_vessel(
        self, db: Session, *, vessel_id: int, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports for a vessel."""
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

    def get_by_report_type(
        self, 
        db: Session, 
        *, 
        report_type: str,
        organization_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Report]:
        """Get reports by type for organization."""
        from app.db.models.project import Project
        
        return (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(
                and_(
                    self.model.report_type == report_type,
                    Project.organization_id == organization_id
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports for a project."""
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

    def get_by_calculation(
        self, db: Session, *, calculation_id: int, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports for a calculation."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.calculation_id == calculation_id,
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_inspection(
        self, db: Session, *, inspection_id: int, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports for an inspection."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.inspection_id == inspection_id,
                    self.model.is_active == True
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent_reports(
        self, 
        db: Session, 
        *, 
        organization_id: int, 
        days: int = 30,
        limit: int = 10
    ) -> List[Report]:
        """Get recent reports for organization."""
        from app.db.models.project import Project
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    self.model.created_at >= cutoff_date
                )
            )
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_pending_reports(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        """Get reports that are still being generated."""
        from app.db.models.project import Project
        
        return (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    self.model.status == "generating"
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_failed_reports(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        """Get failed reports for organization."""
        from app.db.models.project import Project
        
        return (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    self.model.status == "failed"
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
    ) -> List[Report]:
        """Search reports by name, description, or report type."""
        from app.db.models.project import Project
        
        search_term = f"%{query.lower()}%"
        
        return (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    or_(
                        func.lower(self.model.title).contains(search_term),
                        func.lower(self.model.description).contains(search_term),
                        func.lower(self.model.report_type).contains(search_term)
                    )
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_report_statistics(
        self, db: Session, *, organization_id: int
    ) -> Dict[str, Any]:
        """Get report statistics for organization."""
        from app.db.models.project import Project
        
        base_query = (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(Project.organization_id == organization_id)
        )

        total_reports = base_query.count()
        
        completed_reports = base_query.filter(
            self.model.status == "completed"
        ).count()
        
        failed_reports = base_query.filter(
            self.model.status == "failed"
        ).count()
        
        generating_reports = base_query.filter(
            self.model.status == "generating"
        ).count()

        # Calculate by type
        type_stats = (
            base_query
            .with_entities(
                self.model.report_type,
                func.count(self.model.id).label('count')
            )
            .group_by(self.model.report_type)
            .all()
        )
        
        reports_by_type = {stat[0]: stat[1] for stat in type_stats}
        
        # Calculate by format
        format_stats = (
            base_query
            .filter(self.model.status == "completed")
            .with_entities(
                self.model.report_format,
                func.count(self.model.id).label('count')
            )
            .group_by(self.model.report_format)
            .all()
        )
        
        reports_by_format = {stat[0]: stat[1] for stat in format_stats}
        
        # Calculate success rate
        success_rate = (
            (completed_reports / total_reports * 100) 
            if total_reports > 0 else 0
        )

        # Calculate total file size
        total_size = (
            base_query
            .filter(
                and_(
                    self.model.status == "completed",
                    self.model.file_size_bytes.isnot(None)
                )
            )
            .with_entities(func.sum(self.model.file_size_bytes))
            .scalar() or 0
        )

        return {
            "total_reports": total_reports,
            "completed_reports": completed_reports,
            "failed_reports": failed_reports,
            "generating_reports": generating_reports,
            "reports_by_type": reports_by_type,
            "reports_by_format": reports_by_format,
            "success_rate": round(success_rate, 2),
            "total_file_size_mb": round(total_size / (1024 * 1024), 2)
        }

    def update_status(
        self, 
        db: Session, 
        *, 
        report_id: int, 
        status: str,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[Report]:
        """Update report status and file information."""
        report = self.get(db, id=report_id)
        if report:
            update_data = {
                "status": status,
                "generated_at": datetime.utcnow() if status == "completed" else None,
                "error_message": error_message
            }
            
            if file_path:
                update_data["file_path"] = file_path
            if file_size:
                update_data["file_size_bytes"] = file_size
                
            return self.update(db, db_obj=report, obj_in=update_data)
        return None

    def get_report_count_by_vessel(
        self, db: Session, *, vessel_id: int
    ) -> int:
        """Get count of reports for a vessel."""
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

    def get_report_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """Get count of reports for organization."""
        from app.db.models.project import Project
        
        return (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(Project.organization_id == organization_id)
            .count()
        )

    def get_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports for organization."""
        from app.db.models.project import Project
        
        return (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(Project.organization_id == organization_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_downloadable_reports(
        self, 
        db: Session, 
        *, 
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        """Get completed reports that can be downloaded."""
        from app.db.models.project import Project
        
        return (
            db.query(self.model)
            .join(Project, self.model.project_id == Project.id)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    self.model.status == "completed",
                    self.model.file_path.isnot(None)
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def cleanup_old_reports(
        self, 
        db: Session, 
        *, 
        days_old: int = 365
    ) -> int:
        """Mark old reports as inactive for cleanup."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_reports = (
            db.query(self.model)
            .filter(
                and_(
                    self.model.created_at < cutoff_date,
                    self.model.is_active == True
                )
            )
            .all()
        )
        
        count = 0
        for report in old_reports:
            self.soft_delete(db, id=report.id)
            count += 1
            
        return count


report = CRUDReport(Report)
