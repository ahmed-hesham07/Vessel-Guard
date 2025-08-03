"""
Service layer tests for the Vessel Guard application.

Tests for business logic, service orchestration,
and integration between components.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.vessel_service import VesselService
from app.services.calculation_service import CalculationService
from app.services.report_service import ReportService
from app.services.notification_service import NotificationService
from app.services.auth_service import AuthService
from app.services.file_service import FileService

from app.db.models.user import User, UserRole
from app.db.models.organization import Organization
from app.db.models.project import Project, ProjectStatus
from app.db.models.vessel import Vessel
from app.db.models.calculation import Calculation
from app.db.models.report import Report

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.vessel import VesselCreate, VesselUpdate
from app.schemas.calculation import CalculationCreate

from app.core.exceptions import (
    ValidationError,
    PermissionError,
    NotFoundError,
    BusinessLogicError
)


class TestUserService:
    """Test user service functionality."""
    
    def test_create_user_success(self, db_session: Session, test_organization: Organization):
        """Test successful user creation."""
        user_service = UserService(db_session)
        
        user_data = UserCreate(
            email="newuser@example.com",
            password="SecurePass123!",
            first_name="New",
            last_name="User",
            role=UserRole.ENGINEER,
            organization_id=test_organization.id
        )
        
        created_user = user_service.create_user(user_data)
        
        assert created_user.email == "newuser@example.com"
        assert created_user.first_name == "New"
        assert created_user.role == UserRole.ENGINEER
        assert created_user.is_active is True
        assert created_user.hashed_password != "SecurePass123!"  # Should be hashed
    
    def test_create_user_duplicate_email(self, db_session: Session, test_user: User):
        """Test user creation with duplicate email."""
        user_service = UserService(db_session)
        
        user_data = UserCreate(
            email=test_user.email,  # Duplicate email
            password="SecurePass123!",
            first_name="Duplicate",
            last_name="User",
            role=UserRole.ENGINEER,
            organization_id=test_user.organization_id
        )
        
        with pytest.raises(ValidationError, match="Email already registered"):
            user_service.create_user(user_data)
    
    def test_update_user_success(self, db_session: Session, test_user: User):
        """Test successful user update."""
        user_service = UserService(db_session)
        
        update_data = UserUpdate(
            first_name="Updated",
            last_name="Name",
            role=UserRole.ENGINEER
        )
        
        updated_user = user_service.update_user(test_user.id, update_data)
        
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.role == UserRole.ENGINEER
        assert updated_user.email == test_user.email  # Unchanged
    
    def test_get_user_by_email(self, db_session: Session, test_user: User):
        """Test getting user by email."""
        user_service = UserService(db_session)
        
        found_user = user_service.get_user_by_email(test_user.email)
        
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email
    
    def test_get_user_by_email_not_found(self, db_session: Session):
        """Test getting user by email when not found."""
        user_service = UserService(db_session)
        
        found_user = user_service.get_user_by_email("nonexistent@example.com")
        
        assert found_user is None
    
    def test_deactivate_user(self, db_session: Session, test_user: User):
        """Test user deactivation."""
        user_service = UserService(db_session)
        
        deactivated_user = user_service.deactivate_user(test_user.id)
        
        assert deactivated_user.is_active is False
    
    def test_get_organization_members(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test getting organization members."""
        user_service = UserService(db_session)
        
        # Create additional user in the same organization
        additional_user = User(
            email="additional@example.com",
            hashed_password="hashed_password",
            first_name="Additional",
            last_name="User",
            role=UserRole.CONSULTANT,
            organization_id=test_organization.id
        )
        db_session.add(additional_user)
        db_session.commit()
        
        members = user_service.get_organization_members(test_organization.id)
        
        assert len(members) >= 2
        member_emails = [member.email for member in members]
        assert test_user.email in member_emails
        assert additional_user.email in member_emails


class TestProjectService:
    """Test project service functionality."""
    
    def test_create_project_success(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test successful project creation."""
        project_service = ProjectService(db_session)
        
        project_data = ProjectCreate(
            name="New Test Project",
            description="A new test project",
            project_number="NTP-001",
            client_name="Test Client",
            engineering_standards=["ASME VIII", "API 579"],
            design_codes=["ASME VIII Div 1"]
        )
        
        created_project = project_service.create_project(
            project_data,
            organization_id=test_organization.id,
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        assert created_project.name == "New Test Project"
        assert created_project.project_number == "NTP-001"
        assert created_project.status == ProjectStatus.ACTIVE
        assert created_project.organization_id == test_organization.id
        assert created_project.owner_id == test_user.id
    
    def test_create_project_duplicate_number(self, db_session: Session, test_project: Project, test_user: User):
        """Test project creation with duplicate project number."""
        project_service = ProjectService(db_session)
        
        project_data = ProjectCreate(
            name="Duplicate Project",
            project_number=test_project.project_number,  # Duplicate number
            client_name="Test Client"
        )
        
        with pytest.raises(ValidationError, match="Project number already exists"):
            project_service.create_project(
                project_data,
                organization_id=test_project.organization_id,
                owner_id=test_user.id,
                created_by_id=test_user.id
            )
    
    def test_update_project_success(self, db_session: Session, test_project: Project):
        """Test successful project update."""
        project_service = ProjectService(db_session)
        
        update_data = ProjectUpdate(
            name="Updated Project Name",
            description="Updated description",
            status=ProjectStatus.ON_HOLD
        )
        
        updated_project = project_service.update_project(test_project.id, update_data)
        
        assert updated_project.name == "Updated Project Name"
        assert updated_project.description == "Updated description"
        assert updated_project.status == ProjectStatus.ON_HOLD
    
    def test_get_organization_projects(self, db_session: Session, test_organization: Organization, test_project: Project):
        """Test getting organization projects."""
        project_service = ProjectService(db_session)
        
        projects = project_service.get_organization_projects(test_organization.id)
        
        assert len(projects) >= 1
        project_ids = [project.id for project in projects]
        assert test_project.id in project_ids
    
    def test_archive_project(self, db_session: Session, test_project: Project):
        """Test project archival."""
        project_service = ProjectService(db_session)
        
        archived_project = project_service.archive_project(test_project.id)
        
        assert archived_project.status == ProjectStatus.ARCHIVED
        assert archived_project.is_active is False


class TestVesselService:
    """Test vessel service functionality."""
    
    def test_create_vessel_success(self, db_session: Session, test_project: Project, test_material, test_user: User):
        """Test successful vessel creation."""
        vessel_service = VesselService(db_session)
        
        vessel_data = VesselCreate(
            tag_number="V-201",
            name="Test Reactor",
            description="Test reactor vessel",
            vessel_type="pressure_vessel",
            service="Chemical reaction",
            design_pressure=200.0,
            design_temperature=400.0,
            inside_diameter=60.0,
            wall_thickness=0.5,
            design_code="ASME VIII Div 1",
            material_id=test_material.id
        )
        
        created_vessel = vessel_service.create_vessel(
            vessel_data,
            project_id=test_project.id,
            organization_id=test_project.organization_id,
            created_by_id=test_user.id
        )
        
        assert created_vessel.tag_number == "V-201"
        assert created_vessel.name == "Test Reactor"
        assert created_vessel.design_pressure == 200.0
        assert created_vessel.project_id == test_project.id
        assert created_vessel.material_id == test_material.id
    
    def test_update_vessel_success(self, db_session: Session, test_vessel: Vessel):
        """Test successful vessel update."""
        vessel_service = VesselService(db_session)
        
        update_data = VesselUpdate(
            name="Updated Vessel Name",
            design_pressure=175.0,
            operating_pressure=150.0
        )
        
        updated_vessel = vessel_service.update_vessel(test_vessel.id, update_data)
        
        assert updated_vessel.name == "Updated Vessel Name"
        assert updated_vessel.design_pressure == 175.0
        assert updated_vessel.operating_pressure == 150.0
    
    def test_get_project_vessels(self, db_session: Session, test_project: Project, test_vessel: Vessel):
        """Test getting project vessels."""
        vessel_service = VesselService(db_session)
        
        vessels = vessel_service.get_project_vessels(test_project.id)
        
        assert len(vessels) >= 1
        vessel_ids = [vessel.id for vessel in vessels]
        assert test_vessel.id in vessel_ids
    
    def test_vessel_validation(self, db_session: Session, test_project: Project, test_user: User):
        """Test vessel input validation."""
        vessel_service = VesselService(db_session)
        
        # Test invalid design pressure
        vessel_data = VesselCreate(
            tag_number="V-INVALID",
            name="Invalid Vessel",
            vessel_type="pressure_vessel",
            design_pressure=-50.0,  # Invalid negative pressure
            design_temperature=350.0,
            inside_diameter=48.0,
            wall_thickness=0.25,
            design_code="ASME VIII Div 1"
        )
        
        with pytest.raises(ValidationError, match="Design pressure must be positive"):
            vessel_service.create_vessel(
                vessel_data,
                project_id=test_project.id,
                organization_id=test_project.organization_id,
                created_by_id=test_user.id
            )


class TestCalculationService:
    """Test calculation service functionality."""
    
    def test_create_calculation_success(self, db_session: Session, test_vessel: Vessel, test_user: User):
        """Test successful calculation creation."""
        calculation_service = CalculationService(db_session)
        
        calculation_data = CalculationCreate(
            name="Wall Thickness Analysis",
            calculation_type="pressure_vessel_thickness",
            description="ASME VIII wall thickness calculation",
            input_parameters={
                "design_pressure": 150.0,
                "inside_diameter": 48.0,
                "allowable_stress": 20000.0,
                "joint_efficiency": 1.0,
                "corrosion_allowance": 0.125
            }
        )
        
        created_calculation = calculation_service.create_calculation(
            calculation_data,
            vessel_id=test_vessel.id,
            project_id=test_vessel.project_id,
            organization_id=test_vessel.organization_id,
            performed_by_id=test_user.id
        )
        
        assert created_calculation.name == "Wall Thickness Analysis"
        assert created_calculation.calculation_type == "pressure_vessel_thickness"
        assert created_calculation.vessel_id == test_vessel.id
        assert "design_pressure" in created_calculation.input_parameters
    
    @patch('app.services.calculation_engine.ASMEVIIICalculator')
    def test_perform_calculation_success(self, mock_calculator, db_session: Session, test_vessel: Vessel, test_user: User):
        """Test successful calculation execution."""
        # Mock calculation engine
        mock_instance = Mock()
        mock_instance.calculate_cylindrical_shell_thickness.return_value = {
            'required_thickness': 0.186,
            'minimum_thickness': 0.311,
            'safety_factor': 3.2,
            'governing_calculation': 'ASME VIII Div 1'
        }
        mock_calculator.return_value = mock_instance
        
        calculation_service = CalculationService(db_session)
        
        calculation_data = CalculationCreate(
            name="Test Calculation",
            calculation_type="pressure_vessel_thickness",
            input_parameters={
                "design_pressure": 150.0,
                "inside_diameter": 48.0,
                "allowable_stress": 20000.0,
                "joint_efficiency": 1.0,
                "corrosion_allowance": 0.125
            }
        )
        
        result = calculation_service.perform_calculation(
            calculation_data,
            vessel_id=test_vessel.id,
            project_id=test_vessel.project_id,
            organization_id=test_vessel.organization_id,
            performed_by_id=test_user.id
        )
        
        assert result.status == "completed"
        assert "required_thickness" in result.output_parameters
        assert result.output_parameters["required_thickness"] == 0.186
    
    def test_get_vessel_calculations(self, db_session: Session, test_vessel: Vessel):
        """Test getting vessel calculations."""
        calculation_service = CalculationService(db_session)
        
        # Create test calculation
        calculation = Calculation(
            name="Test Calc",
            calculation_type="test_type",
            vessel_id=test_vessel.id,
            project_id=test_vessel.project_id,
            organization_id=test_vessel.organization_id,
            performed_by_id=test_vessel.created_by_id
        )
        db_session.add(calculation)
        db_session.commit()
        
        calculations = calculation_service.get_vessel_calculations(test_vessel.id)
        
        assert len(calculations) >= 1
        calc_ids = [calc.id for calc in calculations]
        assert calculation.id in calc_ids


class TestReportService:
    """Test report service functionality."""
    
    @patch('app.services.report_generator.PDFGenerator')
    def test_generate_calculation_report(self, mock_pdf_generator, db_session: Session, test_vessel: Vessel, test_user: User):
        """Test calculation report generation."""
        # Mock PDF generator
        mock_instance = Mock()
        mock_instance.generate_calculation_report.return_value = b'PDF content'
        mock_pdf_generator.return_value = mock_instance
        
        report_service = ReportService(db_session)
        
        # Create test calculation
        calculation = Calculation(
            name="Test Calculation",
            calculation_type="pressure_vessel_thickness",
            input_parameters={"design_pressure": 150.0},
            output_parameters={"required_thickness": 0.186},
            status="completed",
            vessel_id=test_vessel.id,
            project_id=test_vessel.project_id,
            organization_id=test_vessel.organization_id,
            performed_by_id=test_user.id
        )
        db_session.add(calculation)
        db_session.commit()
        
        report_data = report_service.generate_calculation_report(
            calculation_id=calculation.id,
            generated_by_id=test_user.id
        )
        
        assert report_data['report_id'] is not None
        assert report_data['file_path'] is not None
        assert report_data['content_type'] == 'application/pdf'
    
    def test_get_project_reports(self, db_session: Session, test_project: Project):
        """Test getting project reports."""
        report_service = ReportService(db_session)
        
        # Create test report
        report = Report(
            title="Test Report",
            report_type="calculation",
            project_id=test_project.id,
            organization_id=test_project.organization_id,
            generated_by_id=test_project.created_by_id,
            file_path="/reports/test_report.pdf"
        )
        db_session.add(report)
        db_session.commit()
        
        reports = report_service.get_project_reports(test_project.id)
        
        assert len(reports) >= 1
        report_ids = [report.id for report in reports]
        assert report.id in report_ids


class TestAuthService:
    """Test authentication service functionality."""
    
    def test_authenticate_user_success(self, db_session: Session, test_user: User):
        """Test successful user authentication."""
        auth_service = AuthService(db_session)
        
        # Set a known password for testing
        from app.core.security import get_password_hash
        test_password = "TestPassword123!"
        test_user.hashed_password = get_password_hash(test_password)
        db_session.commit()
        
        authenticated_user = auth_service.authenticate_user(test_user.email, test_password)
        
        assert authenticated_user is not None
        assert authenticated_user.id == test_user.id
        assert authenticated_user.email == test_user.email
    
    def test_authenticate_user_wrong_password(self, db_session: Session, test_user: User):
        """Test authentication with wrong password."""
        auth_service = AuthService(db_session)
        
        authenticated_user = auth_service.authenticate_user(test_user.email, "wrong_password")
        
        assert authenticated_user is None
    
    def test_authenticate_user_inactive(self, db_session: Session, test_user: User):
        """Test authentication of inactive user."""
        auth_service = AuthService(db_session)
        
        # Deactivate user
        test_user.is_active = False
        db_session.commit()
        
        authenticated_user = auth_service.authenticate_user(test_user.email, "any_password")
        
        assert authenticated_user is None
    
    def test_create_access_token(self, db_session: Session, test_user: User):
        """Test access token creation."""
        auth_service = AuthService(db_session)
        
        token_data = auth_service.create_access_token(
            user_id=test_user.id,
            organization_id=test_user.organization_id
        )
        
        assert token_data['access_token'] is not None
        assert token_data['token_type'] == "bearer"
        assert token_data['expires_in'] > 0
    
    def test_verify_token(self, db_session: Session, test_user: User):
        """Test token verification."""
        auth_service = AuthService(db_session)
        
        # Create token
        token_data = auth_service.create_access_token(
            user_id=test_user.id,
            organization_id=test_user.organization_id
        )
        
        # Verify token
        payload = auth_service.verify_token(token_data['access_token'])
        
        assert payload is not None
        assert payload['user_id'] == test_user.id
        assert payload['organization_id'] == test_user.organization_id


class TestFileService:
    """Test file service functionality."""
    
    @patch('app.services.file_service.boto3')
    def test_upload_file_success(self, mock_boto3, db_session: Session, test_user: User):
        """Test successful file upload."""
        # Mock S3 client
        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client
        
        file_service = FileService(db_session)
        
        # Mock file data
        file_data = b"Test file content"
        file_name = "test_document.pdf"
        content_type = "application/pdf"
        
        uploaded_file = file_service.upload_file(
            file_data=file_data,
            file_name=file_name,
            content_type=content_type,
            organization_id=test_user.organization_id,
            uploaded_by_id=test_user.id,
            file_category="document"
        )
        
        assert uploaded_file['file_id'] is not None
        assert uploaded_file['file_name'] == file_name
        assert uploaded_file['file_size'] == len(file_data)
        assert uploaded_file['content_type'] == content_type
    
    def test_delete_file(self, db_session: Session, test_user: User):
        """Test file deletion."""
        file_service = FileService(db_session)
        
        # This would typically involve creating a file record first
        # and then testing deletion
        with patch.object(file_service, '_delete_from_storage') as mock_delete:
            mock_delete.return_value = True
            
            result = file_service.delete_file(
                file_id="test_file_id",
                user_id=test_user.id
            )
            
            assert result is True


class TestNotificationService:
    """Test notification service functionality."""
    
    @patch('app.services.notification_service.EmailService')
    def test_send_calculation_complete_notification(self, mock_email_service, db_session: Session, test_user: User):
        """Test calculation completion notification."""
        # Mock email service
        mock_email_instance = Mock()
        mock_email_service.return_value = mock_email_instance
        
        notification_service = NotificationService(db_session)
        
        notification_data = {
            'user_id': test_user.id,
            'calculation_name': 'Test Calculation',
            'project_name': 'Test Project',
            'calculation_result': 'completed'
        }
        
        result = notification_service.send_calculation_complete_notification(notification_data)
        
        assert result is True
        mock_email_instance.send_template_email.assert_called_once()
    
    def test_create_in_app_notification(self, db_session: Session, test_user: User):
        """Test in-app notification creation."""
        notification_service = NotificationService(db_session)
        
        notification = notification_service.create_notification(
            user_id=test_user.id,
            title="Test Notification",
            message="This is a test notification",
            notification_type="info",
            metadata={"test": "data"}
        )
        
        assert notification.user_id == test_user.id
        assert notification.title == "Test Notification"
        assert notification.is_read is False
        assert notification.notification_type == "info"


class TestServiceIntegration:
    """Test service integration scenarios."""
    
    def test_complete_project_workflow(self, db_session: Session, test_organization: Organization, test_user: User, test_material):
        """Test complete project workflow from creation to calculation."""
        project_service = ProjectService(db_session)
        vessel_service = VesselService(db_session)
        calculation_service = CalculationService(db_session)
        
        # Create project
        project_data = ProjectCreate(
            name="Integration Test Project",
            project_number="ITP-001",
            client_name="Integration Client"
        )
        
        project = project_service.create_project(
            project_data,
            organization_id=test_organization.id,
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        # Create vessel
        vessel_data = VesselCreate(
            tag_number="V-INT-001",
            name="Integration Vessel",
            vessel_type="pressure_vessel",
            design_pressure=150.0,
            design_temperature=350.0,
            inside_diameter=48.0,
            wall_thickness=0.25,
            design_code="ASME VIII Div 1",
            material_id=test_material.id
        )
        
        vessel = vessel_service.create_vessel(
            vessel_data,
            project_id=project.id,
            organization_id=test_organization.id,
            created_by_id=test_user.id
        )
        
        # Create calculation
        calculation_data = CalculationCreate(
            name="Integration Calculation",
            calculation_type="pressure_vessel_thickness",
            input_parameters={
                "design_pressure": 150.0,
                "inside_diameter": 48.0,
                "allowable_stress": 20000.0
            }
        )
        
        with patch('app.services.calculation_engine.ASMEVIIICalculator') as mock_calc:
            mock_instance = Mock()
            mock_instance.calculate_cylindrical_shell_thickness.return_value = {
                'required_thickness': 0.186,
                'minimum_thickness': 0.311
            }
            mock_calc.return_value = mock_instance
            
            calculation = calculation_service.perform_calculation(
                calculation_data,
                vessel_id=vessel.id,
                project_id=project.id,
                organization_id=test_organization.id,
                performed_by_id=test_user.id
            )
        
        # Verify complete workflow
        assert project.id is not None
        assert vessel.project_id == project.id
        assert calculation.vessel_id == vessel.id
        assert calculation.project_id == project.id
        assert calculation.status == "completed"
    
    def test_permission_checking(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test permission checking across services."""
        # Create another organization and user
        other_org = Organization(
            name="Other Organization",
            subdomain="other-org",
            industry="Other",
            country="USA"
        )
        db_session.add(other_org)
        db_session.commit()
        
        other_user = User(
            email="other@example.com",
            hashed_password="hashed_password",
            first_name="Other",
            last_name="User",
            role=UserRole.ENGINEER,
            organization_id=other_org.id
        )
        db_session.add(other_user)
        db_session.commit()
        
        project_service = ProjectService(db_session)
        
        # Create project in test_organization
        project_data = ProjectCreate(
            name="Permission Test Project",
            project_number="PTP-001",
            client_name="Permission Client"
        )
        
        project = project_service.create_project(
            project_data,
            organization_id=test_organization.id,
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        # Try to access project from other organization - should fail
        with pytest.raises(PermissionError):
            project_service.get_project_with_permission_check(
                project_id=project.id,
                user_id=other_user.id,
                organization_id=other_org.id
            )
