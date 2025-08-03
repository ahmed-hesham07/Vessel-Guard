"""Add audit logs table for security and compliance tracking

Revision ID: add_audit_logs_table
Revises: add_performance_indexes
Create Date: 2024-12-03 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_audit_logs_table'
down_revision = 'add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Create audit logs table and related indexes."""
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        
        # Event identification
        sa.Column('event_type', sa.String(100), nullable=False, index=True),
        sa.Column('event_category', sa.String(50), nullable=False, index=True),
        sa.Column('severity', sa.String(20), nullable=False, index=True),
        
        # Timing
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        
        # User and context
        sa.Column('user_id', sa.Integer(), nullable=True, index=True),
        sa.Column('organization_id', sa.Integer(), nullable=True, index=True),
        sa.Column('session_id', sa.String(255), nullable=True, index=True),
        
        # Request context
        sa.Column('ip_address', sa.String(45), nullable=True, index=True),  # IPv6 support
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_id', sa.String(255), nullable=True, index=True),
        sa.Column('api_endpoint', sa.String(255), nullable=True, index=True),
        sa.Column('http_method', sa.String(10), nullable=True),
        
        # Event details
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        
        # Resource information
        sa.Column('resource_type', sa.String(100), nullable=True, index=True),
        sa.Column('resource_id', sa.String(100), nullable=True, index=True),
        
        # Security
        sa.Column('checksum', sa.String(64), nullable=False),  # SHA-256 hash for integrity
        
        # Status
        sa.Column('is_sensitive', sa.Boolean(), default=False, nullable=False),
        sa.Column('requires_investigation', sa.Boolean(), default=False, nullable=False),
    )
    
    # Create performance indexes
    op.create_index('idx_audit_user_time', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_org_time', 'audit_logs', ['organization_id', 'timestamp'])
    op.create_index('idx_audit_event_time', 'audit_logs', ['event_type', 'timestamp'])
    op.create_index('idx_audit_severity_time', 'audit_logs', ['severity', 'timestamp'])
    op.create_index('idx_audit_ip_time', 'audit_logs', ['ip_address', 'timestamp'])
    op.create_index('idx_audit_investigation', 'audit_logs', ['requires_investigation', 'timestamp'])
    
    # Create composite indexes for common query patterns
    op.create_index('idx_audit_category_severity', 'audit_logs', ['event_category', 'severity'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('idx_audit_sensitive', 'audit_logs', ['is_sensitive', 'timestamp'])
    
    # Create user sessions table for enhanced session management
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('session_id', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('organization_id', sa.Integer(), nullable=True, index=True),
        
        # Session metadata
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_fingerprint', sa.String(255), nullable=True),
        
        # Timing
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        
        # Status
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('logout_reason', sa.String(100), nullable=True),
        
        # Security
        sa.Column('is_trusted_device', sa.Boolean(), default=False, nullable=False),
        sa.Column('two_factor_verified', sa.Boolean(), default=False, nullable=False),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    
    # Indexes for user sessions
    op.create_index('idx_user_sessions_user_active', 'user_sessions', ['user_id', 'is_active', 'last_activity'])
    op.create_index('idx_user_sessions_cleanup', 'user_sessions', ['expires_at', 'is_active'])
    op.create_index('idx_user_sessions_ip', 'user_sessions', ['ip_address', 'created_at'])
    
    # Create security events summary table for fast analytics
    op.create_table(
        'security_events_summary',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('organization_id', sa.Integer(), nullable=True, index=True),
        
        # Event counts
        sa.Column('total_events', sa.Integer(), default=0, nullable=False),
        sa.Column('login_attempts', sa.Integer(), default=0, nullable=False),
        sa.Column('failed_logins', sa.Integer(), default=0, nullable=False),
        sa.Column('suspicious_activities', sa.Integer(), default=0, nullable=False),
        sa.Column('security_violations', sa.Integer(), default=0, nullable=False),
        
        # Top IPs and users (JSON arrays)
        sa.Column('top_source_ips', sa.JSON(), nullable=True),
        sa.Column('top_active_users', sa.JSON(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Unique constraint for date and organization
        sa.UniqueConstraint('date', 'organization_id', name='uq_security_summary_date_org'),
        
        # Foreign key
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    
    # Password history table for password policy enforcement
    op.create_table(
        'password_history',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Foreign key
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Index for password history cleanup
    op.create_index('idx_password_history_user_date', 'password_history', ['user_id', 'created_at'])


def downgrade():
    """Remove audit logs table and related structures."""
    
    # Drop tables in reverse order
    op.drop_table('password_history')
    op.drop_table('security_events_summary')
    op.drop_table('user_sessions')
    op.drop_table('audit_logs')
    
    # Note: Indexes are automatically dropped with the tables