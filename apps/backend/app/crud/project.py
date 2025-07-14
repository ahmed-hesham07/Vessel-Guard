"""
CRUD operations for Project model.

Handles project management including timeline tracking,
collaboration, and organization-based access control.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.project import Project
from app.db.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """
    CRUD operations for Project model.
    
    Extends base CRUD with project-specific methods
    for timeline management and collaboration features.
    """

    def get_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """
        Get projects by organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of projects in organization
        """
        return (
            db.query(Project)
            .filter(Project.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """
        Get active projects by organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of active projects in organization
        """
        return (
            db.query(Project)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    Project.is_active == True
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """
        Get projects by owner.
        
        Args:
            db: Database session
            owner_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of projects owned by user
        """
        return (
            db.query(Project)
            .filter(Project.created_by_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Get projects by status.
        
        Args:
            db: Database session
            status: Project status
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of projects with matching status
        """
        query = db.query(Project).filter(Project.status == status)
        
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        
        return query.offset(skip).limit(limit).all()

    def get_overdue_projects(
        self, db: Session, *, organization_id: Optional[int] = None
    ) -> List[Project]:
        """
        Get projects that are overdue.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            
        Returns:
            List of overdue projects
        """
        query = db.query(Project).filter(
            and_(
                Project.end_date.isnot(None),
                Project.end_date < datetime.utcnow(),
                Project.status.notin_(["completed", "cancelled"])
            )
        )
        
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        
        return query.all()

    def get_due_soon(
        self,
        db: Session,
        *,
        days_ahead: int = 7,
        organization_id: Optional[int] = None
    ) -> List[Project]:
        """
        Get projects due soon.
        
        Args:
            db: Database session
            days_ahead: Number of days to look ahead
            organization_id: Optional organization filter
            
        Returns:
            List of projects due within specified days
        """
        from datetime import timedelta
        
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        query = db.query(Project).filter(
            and_(
                Project.end_date.isnot(None),
                Project.end_date <= future_date,
                Project.end_date >= datetime.utcnow(),
                Project.status.notin_(["completed", "cancelled"])
            )
        )
        
        if organization_id:
            query = query.filter(Project.organization_id == organization_id)
        
        return query.all()

    def search(
        self,
        db: Session,
        *,
        query: str,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Search projects by name or description.
        
        Args:
            db: Database session
            query: Search query
            organization_id: Optional organization filter
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of matching projects
        """
        search_term = f"%{query}%"
        db_query = db.query(Project).filter(
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term),
                Project.project_number.ilike(search_term)
            )
        )
        
        if organization_id:
            db_query = db_query.filter(Project.organization_id == organization_id)
        
        return db_query.offset(skip).limit(limit).all()

    def get_by_project_number(
        self, db: Session, *, project_number: str, organization_id: int
    ) -> Optional[Project]:
        """
        Get project by project number within organization.
        
        Args:
            db: Database session
            project_number: Project number
            organization_id: Organization ID
            
        Returns:
            Project if found, None otherwise
        """
        return (
            db.query(Project)
            .filter(
                and_(
                    Project.project_number == project_number,
                    Project.organization_id == organization_id
                )
            )
            .first()
        )

    def update_status(
        self, db: Session, *, project_id: int, status: str, updated_by_id: int
    ) -> Project:
        """
        Update project status.
        
        Args:
            db: Database session
            project_id: Project ID
            status: New status
            updated_by_id: User ID making the update
            
        Returns:
            Updated project
        """
        project = self.get_or_404(db, id=project_id)
        
        project.status = status
        project.updated_by_id = updated_by_id
        project.updated_at = datetime.utcnow()
        
        # Set completion date if completed
        if status == "completed" and not project.actual_end_date:
            project.actual_end_date = datetime.utcnow()
        
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def complete_project(
        self, db: Session, *, project_id: int, completed_by_id: int
    ) -> Project:
        """
        Mark project as completed.
        
        Args:
            db: Database session
            project_id: Project ID
            completed_by_id: User ID completing the project
            
        Returns:
            Completed project
        """
        return self.update_status(
            db, project_id=project_id, status="completed", updated_by_id=completed_by_id
        )

    def get_project_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """
        Get total project count for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Total project count
        """
        return (
            db.query(func.count(Project.id))
            .filter(Project.organization_id == organization_id)
            .scalar()
        )

    def get_active_project_count_by_organization(
        self, db: Session, *, organization_id: int
    ) -> int:
        """
        Get active project count for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Active project count
        """
        return (
            db.query(func.count(Project.id))
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    Project.is_active == True
                )
            )
            .scalar()
        )

    def can_create_project(self, db: Session, *, organization_id: int) -> bool:
        """
        Check if organization can create a new project.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            True if organization can create projects, False otherwise
        """
        from app.crud.organization import organization as org_crud
        
        org = org_crud.get(db, id=organization_id)
        if not org or not org.is_active:
            return False
        
        # Check project limit
        if org.max_projects:
            current_count = self.get_active_project_count_by_organization(
                db, organization_id=organization_id
            )
            if current_count >= org.max_projects:
                return False
        
        return True

    def get_recent_projects(
        self,
        db: Session,
        *,
        organization_id: int,
        days: int = 30,
        limit: int = 10
    ) -> List[Project]:
        """
        Get recently created projects.
        
        Args:
            db: Database session
            organization_id: Organization ID
            days: Number of days to look back
            limit: Maximum projects to return
            
        Returns:
            List of recent projects
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db.query(Project)
            .filter(
                and_(
                    Project.organization_id == organization_id,
                    Project.created_at >= cutoff_date
                )
            )
            .order_by(Project.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_project_statistics(
        self, db: Session, *, organization_id: int
    ) -> dict:
        """
        Get project statistics for organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            
        Returns:
            Dictionary with project statistics
        """
        total_projects = self.get_project_count_by_organization(
            db, organization_id=organization_id
        )
        active_projects = self.get_active_project_count_by_organization(
            db, organization_id=organization_id
        )
        
        # Count by status
        status_counts = {}
        for status in ["planning", "in_progress", "review", "completed", "cancelled"]:
            count = (
                db.query(func.count(Project.id))
                .filter(
                    and_(
                        Project.organization_id == organization_id,
                        Project.status == status
                    )
                )
                .scalar()
            )
            status_counts[status] = count
        
        overdue_count = len(self.get_overdue_projects(db, organization_id=organization_id))
        due_soon_count = len(self.get_due_soon(db, organization_id=organization_id))
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "status_breakdown": status_counts,
            "overdue_projects": overdue_count,
            "due_soon_projects": due_soon_count
        }


# Create instance for dependency injection
project = CRUDProject(Project)
