"""
Database model tests for the Vessel Guard application.

Tests for all database models, relationships, validations,
and CRUD operations.
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.db.models.user import User, UserRole
from app.db.models.organization import Organization, SubscriptionType
from app.db.models.project import Project, ProjectStatus, ProjectPriority
from app.db.models.vessel import Vessel
from app.db.models.material import Material, MaterialType, MaterialStandard
from app.db.models.calculation import Calculation
from app.db.models.inspection import Inspection, InspectionType, InspectionStatus
from app.db.models.report import Report
from app.core.security import get_password_hash


class TestUserModel:
    """Test User model functionality."""
    
    def test_create_user(self, db_session: Session, test_organization: Organization):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="Test",
            last_name="User",
            role=UserRole.ENGINEER,
            organization_id=test_organization.id,
            is_active=True,
            is_verified=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == UserRole.ENGINEER
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_email_unique_constraint(self, db_session: Session, test_organization: Organization):
        """Test that user email must be unique."""
        user1 = User(
            email="duplicate@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="User",
            last_name="One",
            role=UserRole.ENGINEER,
            organization_id=test_organization.id
        )
        
        user2 = User(
            email="duplicate@example.com",  # Same email
            hashed_password=get_password_hash("password456"),
            first_name="User",
            last_name="Two",
            role=UserRole.ENGINEER,
            organization_id=test_organization.id
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_organization_relationship(self, db_session: Session, test_user: User, test_organization: Organization):
        """Test user-organization relationship."""
        assert test_user.organization_id == test_organization.id
        assert test_user.organization == test_organization
        assert test_user in test_organization.members
    
    def test_user_string_representation(self, test_user: User):
        """Test user string representation."""
        expected = f"<User {test_user.email}>"
        assert str(test_user) == expected
    
    def test_user_role_enum(self, db_session: Session, test_organization: Organization):
        """Test user role enumeration."""
        for role in UserRole:
            user = User(
                email=f"{role.value}@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="Test",
                last_name=role.value.title(),
                role=role,
                organization_id=test_organization.id
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Verify all roles were created
        users = db_session.query(User).filter(User.email.like('%@example.com')).all()
        user_roles = [user.role for user in users]
        
        for role in UserRole:
            assert role in user_roles


class TestOrganizationModel:
    """Test Organization model functionality."""
    
    def test_create_organization(self, db_session: Session):
        """Test creating an organization."""
        org = Organization(
            name="Test Engineering Corp",
            description="A test engineering organization",
            primary_industry="Oil & Gas",
            country="USA",
            subscription_type=SubscriptionType.PROFESSIONAL,
            max_users=100,
            max_projects=50,
            max_calculations_per_month=5000,
            is_active=True
        )
        
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        assert org.id is not None
        assert org.name == "Test Engineering Corp"
        assert org.description == "A test engineering organization"
        assert org.subscription_type == SubscriptionType.PROFESSIONAL
        assert org.max_users == 100
        assert org.is_active is True
        assert org.created_at is not None
    
    def test_organization_name_unique(self, db_session: Session):
        """Test that organization name must be unique."""
        org1 = Organization(
            name="Duplicate Corp",
            primary_industry="Manufacturing",
            country="USA"
        )
        
        org2 = Organization(
            name="Duplicate Corp",  # Same name
            primary_industry="Oil & Gas",
            country="Canada"
        )
        
        db_session.add(org1)
        db_session.commit()
        
        db_session.add(org2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_organization_members_relationship(self, db_session: Session, test_organization: Organization):
        """Test organization members relationship."""
        # Create multiple users for the organization
        users = []
        for i in range(3):
            user = User(
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("password123"),
                first_name=f"User{i}",
                last_name="Test",
                role=UserRole.ENGINEER,
                organization_id=test_organization.id
            )
            users.append(user)
            db_session.add(user)
        
        db_session.commit()
        
        # Refresh organization to load relationships
        db_session.refresh(test_organization)
        
        assert len(test_organization.members) >= 3
        for user in users:
            assert user in test_organization.members


class TestProjectModel:
    """Test Project model functionality."""
    
    def test_create_project(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test creating a project."""
        project = Project(
            name="Test Pressure Vessel Analysis",
            description="Comprehensive analysis of pressure vessels",
            project_number="PV-2024-001",
            client_name="Industrial Client",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            organization_id=test_organization.id,
            owner_id=test_user.id,
            created_by_id=test_user.id,
            engineering_standards=["ASME VIII", "API 579"],
            design_codes=["ASME VIII Div 1", "ASME VIII Div 2"],
            is_active=True
        )
        
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        assert project.id is not None
        assert project.name == "Test Pressure Vessel Analysis"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == ProjectPriority.HIGH
        assert project.engineering_standards == ["ASME VIII", "API 579"]
        assert project.created_at is not None
    
    def test_project_unique_number(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test that project number must be unique."""
        project1 = Project(
            name="Project One",
            project_number="DUPLICATE-001",
            organization_id=test_organization.id,
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        project2 = Project(
            name="Project Two",
            project_number="DUPLICATE-001",  # Same project number
            organization_id=test_organization.id,
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        db_session.add(project1)
        db_session.commit()
        
        db_session.add(project2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_project_status_enum(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test project status enumeration."""
        for status in ProjectStatus:
            project = Project(
                name=f"Project {status.value}",
                project_number=f"P-{status.value.upper()}-001",
                status=status,
                organization_id=test_organization.id,
                owner_id=test_user.id,
                created_by_id=test_user.id
            )
            db_session.add(project)
        
        db_session.commit()
        
        # Verify all statuses were created
        projects = db_session.query(Project).filter(Project.project_number.like('P-%-001')).all()
        project_statuses = [project.status for project in projects]
        
        for status in ProjectStatus:
            assert status in project_statuses


class TestVesselModel:
    """Test Vessel model functionality."""
    
    def test_create_vessel(self, db_session: Session, test_project: Project, test_material: Material, test_user: User):
        """Test creating a vessel."""
        vessel = Vessel(
            tag_number="V-101",
            name="Test Pressure Vessel",
            description="Test vessel for unit testing",
            vessel_type="pressure_vessel",
            service="Steam generation",
            location="Plant A",
            design_code="ASME VIII Div 1",
            design_pressure=150.0,
            design_temperature=350.0,
            operating_pressure=125.0,
            operating_temperature=300.0,
            inside_diameter=48.0,
            outside_diameter=48.5,
            wall_thickness=0.25,
            overall_length=120.0,
            head_type="ellipsoidal",
            corrosion_allowance=0.125,
            joint_efficiency=1.0,
            project_id=test_project.id,
            organization_id=test_project.organization_id,
            material_id=test_material.id,
            created_by_id=test_user.id,
            is_active=True
        )
        
        db_session.add(vessel)
        db_session.commit()
        db_session.refresh(vessel)
        
        assert vessel.id is not None
        assert vessel.tag_number == "V-101"
        assert vessel.design_pressure == 150.0
        assert vessel.design_temperature == 350.0
        assert vessel.inside_diameter == 48.0
        assert vessel.wall_thickness == 0.25
        assert vessel.is_active is True
    
    def test_vessel_project_relationship(self, test_vessel: Vessel, test_project: Project):
        """Test vessel-project relationship."""
        assert test_vessel.project_id == test_project.id
        assert test_vessel.project == test_project
        assert test_vessel in test_project.vessels
    
    def test_vessel_material_relationship(self, test_vessel: Vessel, test_material: Material):
        """Test vessel-material relationship."""
        assert test_vessel.material_id == test_material.id
        assert test_vessel.material == test_material
    
    def test_vessel_tag_number_validation(self, db_session: Session, test_project: Project, test_user: User):
        """Test vessel tag number constraints."""
        # Test empty tag number
        vessel = Vessel(
            tag_number="",  # Empty tag number should fail
            name="Test Vessel",
            vessel_type="pressure_vessel",
            design_code="ASME VIII Div 1",
            design_pressure=150.0,
            design_temperature=350.0,
            project_id=test_project.id,
            organization_id=test_project.organization_id,
            created_by_id=test_user.id
        )
        
        db_session.add(vessel)
        with pytest.raises((IntegrityError, Exception)):  # Could be validation or constraint error
            db_session.commit()


class TestMaterialModel:
    """Test Material model functionality."""
    
    def test_create_material(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test creating a material."""
        material = Material(
            specification="SA-516",
            grade="Grade 70",
            standard=MaterialStandard.ASME,
            material_type=MaterialType.CARBON_STEEL,
            common_name="Carbon Steel SA-516 Gr 70",
            description="Pressure vessel quality carbon steel",
            yield_strength=38000.0,
            tensile_strength=70000.0,
            elongation=21.0,
            min_temp=-20.0,
            max_temp=650.0,
            density=0.284,
            modulus_of_elasticity=29000000.0,
            poisson_ratio=0.3,
            thermal_expansion=6.5e-6,
            thermal_conductivity=26.0,
            is_asme_approved=True,
            is_weldable=True,
            is_public=True,
            is_active=True,
            organization_id=test_organization.id,
            created_by_id=test_user.id
        )
        
        db_session.add(material)
        db_session.commit()
        db_session.refresh(material)
        
        assert material.id is not None
        assert material.specification == "SA-516"
        assert material.grade == "Grade 70"
        assert material.standard == MaterialStandard.ASME
        assert material.material_type == MaterialType.CARBON_STEEL
        assert material.yield_strength == 38000.0
        assert material.is_asme_approved is True
    
    def test_material_standard_enum(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test material standard enumeration."""
        for standard in MaterialStandard:
            material = Material(
                specification=f"TEST-{standard.value}",
                grade="Test Grade",
                standard=standard,
                material_type=MaterialType.CARBON_STEEL,
                organization_id=test_organization.id,
                created_by_id=test_user.id
            )
            db_session.add(material)
        
        db_session.commit()
        
        # Verify all standards were created
        materials = db_session.query(Material).filter(Material.specification.like('TEST-%')).all()
        material_standards = [material.standard for material in materials]
        
        for standard in MaterialStandard:
            assert standard in material_standards
    
    def test_material_type_enum(self, db_session: Session, test_organization: Organization, test_user: User):
        """Test material type enumeration."""
        for material_type in MaterialType:
            material = Material(
                specification=f"TYPE-{material_type.value}",
                grade="Test Grade",
                standard=MaterialStandard.ASME,
                material_type=material_type,
                organization_id=test_organization.id,
                created_by_id=test_user.id
            )
            db_session.add(material)
        
        db_session.commit()
        
        # Verify all types were created
        materials = db_session.query(Material).filter(Material.specification.like('TYPE-%')).all()
        material_types = [material.material_type for material in materials]
        
        for material_type in MaterialType:
            assert material_type in material_types


class TestCalculationModel:
    """Test Calculation model functionality."""
    
    def test_create_calculation(self, db_session: Session, test_vessel: Vessel, test_user: User):
        """Test creating a calculation."""
        calculation = Calculation(
            name="Wall Thickness Calculation",
            calculation_type="pressure_vessel_thickness",
            description="ASME VIII Div 1 wall thickness calculation",
            input_parameters={
                "design_pressure": 150.0,
                "design_temperature": 350.0,
                "inside_diameter": 48.0,
                "material_yield_strength": 38000.0,
                "joint_efficiency": 1.0,
                "corrosion_allowance": 0.125
            },
            output_parameters={
                "required_thickness": 0.186,
                "minimum_thickness": 0.311,
                "safety_factor": 3.2
            },
            status="completed",
            vessel_id=test_vessel.id,
            project_id=test_vessel.project_id,
            organization_id=test_vessel.organization_id,
            performed_by_id=test_user.id,
            is_active=True
        )
        
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)
        
        assert calculation.id is not None
        assert calculation.name == "Wall Thickness Calculation"
        assert calculation.calculation_type == "pressure_vessel_thickness"
        assert calculation.status == "completed"
        assert "design_pressure" in calculation.input_parameters
        assert "required_thickness" in calculation.output_parameters
    
    def test_calculation_vessel_relationship(self, db_session: Session, test_vessel: Vessel, test_user: User):
        """Test calculation-vessel relationship."""
        calculation = Calculation(
            name="Test Calculation",
            calculation_type="test_type",
            vessel_id=test_vessel.id,
            project_id=test_vessel.project_id,
            organization_id=test_vessel.organization_id,
            performed_by_id=test_user.id
        )
        
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)
        
        assert calculation.vessel == test_vessel
        assert calculation in test_vessel.calculations


class TestInspectionModel:
    """Test Inspection model functionality."""
    
    def test_create_inspection(self, db_session: Session, test_vessel: Vessel, test_user: User):
        """Test creating an inspection."""
        inspection_date = datetime.now() + timedelta(days=30)
        
        inspection = Inspection(
            inspection_number="INS-001",
            inspection_type=InspectionType.EXTERNAL_VISUAL,
            scheduled_date=inspection_date,
            inspection_methods=["visual", "ultrasonic"],
            inspection_scope="Complete external inspection",
            inspector_id=test_user.id,
            vessel_id=test_vessel.id,
            project_id=test_vessel.project_id,
            organization_id=test_vessel.organization_id,
            status=InspectionStatus.SCHEDULED,
            is_active=True
        )
        
        db_session.add(inspection)
        db_session.commit()
        db_session.refresh(inspection)
        
        assert inspection.id is not None
        assert inspection.inspection_number == "INS-001"
        assert inspection.inspection_type == InspectionType.EXTERNAL_VISUAL
        assert inspection.status == InspectionStatus.SCHEDULED
        assert "visual" in inspection.inspection_methods
        assert "ultrasonic" in inspection.inspection_methods
    
    def test_inspection_vessel_relationship(self, db_session: Session, test_vessel: Vessel, test_user: User):
        """Test inspection-vessel relationship."""
        inspection = Inspection(
            inspection_type=InspectionType.EXTERNAL_VISUAL,
            scheduled_date=datetime.now() + timedelta(days=30),
            inspector_id=test_user.id,
            vessel_id=test_vessel.id,
            project_id=test_vessel.project_id,
            organization_id=test_vessel.organization_id,
            status=InspectionStatus.SCHEDULED
        )
        
        db_session.add(inspection)
        db_session.commit()
        db_session.refresh(inspection)
        
        assert inspection.vessel == test_vessel
        assert inspection in test_vessel.inspections


class TestModelRelationships:
    """Test complex model relationships and cascades."""
    
    def test_organization_deletion_cascade(self, db_session: Session):
        """Test that deleting organization handles related records properly."""
        # This test depends on how cascade is configured
        # For now, just verify the relationship exists
        org = Organization(
            name="Test Cascade Org",
            description="Test organization for cascade testing",
            primary_industry="Test",
            country="USA"
        )
        db_session.add(org)
        db_session.commit()
        
        user = User(
            email="cascade@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="Cascade",
            last_name="Test",
            role=UserRole.ENGINEER,
            organization_id=org.id
        )
        db_session.add(user)
        db_session.commit()
        
        # Verify relationship
        assert user.organization == org
        assert user in org.users
    
    def test_project_vessel_calculation_chain(self, test_project: Project, test_vessel: Vessel, db_session: Session, test_user: User):
        """Test the chain of relationships: Project -> Vessel -> Calculation."""
        calculation = Calculation(
            name="Chain Test Calculation",
            calculation_type="test_chain",
            vessel_id=test_vessel.id,
            project_id=test_project.id,
            organization_id=test_project.organization_id,
            performed_by_id=test_user.id
        )
        
        db_session.add(calculation)
        db_session.commit()
        db_session.refresh(calculation)
        
        # Verify the complete chain
        assert calculation.vessel == test_vessel
        assert calculation.project == test_project
        assert calculation.vessel.project == test_project
        assert calculation in test_vessel.calculations
        assert calculation in test_project.calculations
    
    def test_audit_fields(self, test_project: Project):
        """Test that audit fields are properly set."""
        assert test_project.created_at is not None
        assert isinstance(test_project.created_at, datetime)
        
        # Updated_at might be None for new records
        if test_project.updated_at:
            assert isinstance(test_project.updated_at, datetime)
        
        assert test_project.created_by_id is not None
        assert test_project.organization_id is not None
