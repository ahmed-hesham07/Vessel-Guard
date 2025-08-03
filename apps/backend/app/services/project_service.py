"""
Project service layer for handling project-related business logic.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models.project import Project, ProjectStatus, ProjectPriority
from app.db.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.exceptions import ValidationError, NotFoundError, PermissionError


class ProjectService:
    """Service class for project operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_project(self, project_data: ProjectCreate, organization_id: int, 
                      owner_id: int, created_by_id: int) -> Project:
        """Create a new project."""
        # Check if project number already exists
        if project_data.project_number:
            existing = self.db.query(Project).filter(
                Project.project_number == project_data.project_number,
                Project.organization_id == organization_id
            ).first()
            if existing:
                raise ValidationError("Project number already exists")
        
        db_project = Project(
            **project_data.dict(),
            organization_id=organization_id,
            owner_id=owner_id,
            created_by_id=created_by_id,
            status=ProjectStatus.ACTIVE,
            is_active=True
        )
        
        try:
            self.db.add(db_project)
            self.db.commit()
            self.db.refresh(db_project)
            return db_project
        except IntegrityError:
            self.db.rollback()
            raise ValidationError("Project creation failed")
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def update_project(self, project_id: int, project_data: ProjectUpdate) -> Project:
        """Update project."""
        project = self.get_project_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def archive_project(self, project_id: int) -> Project:
        """Archive a project."""
        project = self.get_project_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        project.status = ProjectStatus.ARCHIVED
        project.is_active = False
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_organization_projects(self, organization_id: int) -> List[Project]:
        """Get all projects for an organization."""
        return self.db.query(Project).filter(
            Project.organization_id == organization_id
        ).all()
    
    def get_project_with_permission_check(self, project_id: int, user_id: int, 
                                        organization_id: int) -> Project:
        """Get project with permission check."""
        project = self.get_project_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        
        if project.organization_id != organization_id:
            raise PermissionError("Access denied")
        
        return project
