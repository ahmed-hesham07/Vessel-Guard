"""Add performance indexes for common query patterns

Revision ID: add_performance_indexes
Revises: 8a677d0cf7fe
Create Date: 2024-12-03 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = '8a677d0cf7fe_add_tickets_table'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes for common query patterns."""
    
    # Calculations table - common query patterns
    op.create_index(
        'idx_calculations_org_type', 
        'calculations', 
        ['calculation_type', 'created_at']
    )
    op.create_index(
        'idx_calculations_vessel_status', 
        'calculations', 
        ['vessel_id', 'status', 'is_active']
    )
    op.create_index(
        'idx_calculations_project_active', 
        'calculations', 
        ['project_id', 'is_active', 'created_at']
    )
    op.create_index(
        'idx_calculations_user_date', 
        'calculations', 
        ['calculated_by_id', 'created_at']
    )
    
    # Users table - authentication and organization queries
    op.create_index(
        'idx_users_org_role', 
        'users', 
        ['organization_id', 'role', 'is_active']
    )
    op.create_index(
        'idx_users_org_active', 
        'users', 
        ['organization_id', 'is_active']
    )
    
    # Projects table - organization and status queries
    op.create_index(
        'idx_projects_org_status', 
        'projects', 
        ['organization_id', 'status', 'is_active']
    )
    op.create_index(
        'idx_projects_org_priority', 
        'projects', 
        ['organization_id', 'priority', 'created_at']
    )
    
    # Vessels table - project and organization queries
    op.create_index(
        'idx_vessels_project_active', 
        'vessels', 
        ['project_id', 'is_active']
    )
    op.create_index(
        'idx_vessels_org_type', 
        'vessels', 
        ['organization_id', 'vessel_type']
    )
    
    # Inspections table - vessel and date queries
    op.create_index(
        'idx_inspections_vessel_date', 
        'inspections', 
        ['vessel_id', 'scheduled_date']
    )
    op.create_index(
        'idx_inspections_status_date', 
        'inspections', 
        ['status', 'scheduled_date']
    )
    op.create_index(
        'idx_inspections_inspector_date', 
        'inspections', 
        ['inspector_id', 'scheduled_date']
    )
    
    # Reports table - project and status queries
    op.create_index(
        'idx_reports_project_status', 
        'reports', 
        ['project_id', 'status', 'created_at']
    )
    op.create_index(
        'idx_reports_vessel_type', 
        'reports', 
        ['vessel_id', 'report_type', 'created_at']
    )
    
    # Materials table - standard and grade queries
    op.create_index(
        'idx_materials_standard_grade', 
        'materials', 
        ['standard', 'grade']
    )
    op.create_index(
        'idx_materials_active_temp', 
        'materials', 
        ['is_active', 'max_temperature']
    )
    
    # Session management optimization
    op.create_index(
        'idx_user_sessions_user_active', 
        'user_sessions', 
        ['user_id', 'is_active', 'last_activity']
    )
    op.create_index(
        'idx_user_sessions_cleanup', 
        'user_sessions', 
        ['expires_at', 'is_active']
    )


def downgrade():
    """Remove performance indexes."""
    
    # Remove all the indexes we created
    indexes_to_drop = [
        'idx_calculations_org_type',
        'idx_calculations_vessel_status',
        'idx_calculations_project_active',
        'idx_calculations_user_date',
        'idx_users_org_role',
        'idx_users_org_active',
        'idx_projects_org_status',
        'idx_projects_org_priority',
        'idx_vessels_project_active',
        'idx_vessels_org_type',
        'idx_inspections_vessel_date',
        'idx_inspections_status_date',
        'idx_inspections_inspector_date',
        'idx_reports_project_status',
        'idx_reports_vessel_type',
        'idx_materials_standard_grade',
        'idx_materials_active_temp',
        'idx_user_sessions_user_active',
        'idx_user_sessions_cleanup'
    ]
    
    for index_name in indexes_to_drop:
        try:
            op.drop_index(index_name)
        except Exception:
            # Index might not exist, continue
            pass