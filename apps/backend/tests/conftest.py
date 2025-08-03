"""
Test configuration and fixtures for the Vessel Guard application.

This module provides common test configuration, database setup,
and reusable fixtures for all test modules.
"""

import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.core.config import settings
from app.db.models.user import User
from app.db.models.organization import Organization, SubscriptionType
from app.db.models.project import Project
from app.db.models.vessel import Vessel
from app.db.models.material import Material
from app.core.security import get_password_hash


# Test database URL - use SQLite for fast tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL debugging
)

# Test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with dependency overrides."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_organization(db_session: Session) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Engineering Corp",
        description="A test engineering organization",
        website="https://testeng.com",
        primary_industry="Oil & Gas",
        country="USA",
        subscription_type=SubscriptionType.PROFESSIONAL,
        max_users=50,
        max_projects=20,
        max_calculations_per_month=1000,
        is_active=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def test_user(db_session: Session, test_organization: Organization) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="Engineer",
        role="admin",
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_project(db_session: Session, test_organization: Organization, test_user: User) -> Project:
    """Create a test project."""
    project = Project(
        name="Test Pressure Vessel Project",
        description="A test project for pressure vessel analysis",
        project_number="P-001",
        client_name="Test Client",
        status="active",
        priority="high",
        organization_id=test_organization.id,
        owner_id=test_user.id,
        created_by_id=test_user.id,
        engineering_standards=["ASME VIII", "ASME B31.3"],
        design_codes=["ASME VIII Div 1"],
        default_units="imperial",
        is_active=True
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_material(db_session: Session, test_organization: Organization, test_user: User) -> Material:
    """Create a test material."""
    material = Material(
        specification="SA-516",
        grade="Grade 70",
        standard="ASME",
        material_type="carbon_steel",
        common_name="Carbon Steel SA-516 Gr 70",
        description="Pressure vessel quality carbon steel",
        yield_strength=38000.0,
        tensile_strength=70000.0,
        min_temp=-20.0,
        max_temp=650.0,
        density=0.284,
        modulus_of_elasticity=29000000.0,
        poisson_ratio=0.3,
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
    return material


@pytest.fixture
def test_vessel(db_session: Session, test_project: Project, test_material: Material, test_user: User) -> Vessel:
    """Create a test vessel."""
    vessel = Vessel(
        tag_number="V-101",
        name="Test Pressure Vessel",
        description="A test pressure vessel for calculations",
        vessel_type="pressure_vessel",
        service="Steam generation",
        location="Plant A, Unit 1",
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
    return vessel


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for API requests."""
    from app.core.security import create_access_token
    access_token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_user(db_session: Session, test_organization: Organization) -> User:
    """Create a test admin user."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        first_name="Admin",
        last_name="User",
        role="admin",
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True,
        is_superuser=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def viewer_user(db_session: Session, test_organization: Organization) -> User:
    """Create a test viewer user."""
    user = User(
        email="viewer@example.com",
        hashed_password=get_password_hash("viewerpassword123"),
        first_name="Viewer",
        last_name="User",
        role="viewer",
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_organization(db_session: Session, **kwargs) -> Organization:
        """Create a test organization with custom parameters."""
        defaults = {
            "name": "Test Organization",
            "subdomain": "test-org",
            "industry": "Manufacturing",
            "country": "USA",
            "subscription_tier": "basic",
            "max_members": 10,
            "max_projects": 5,
            "max_calculations_per_month": 100,
            "is_active": True
        }
        defaults.update(kwargs)
        
        org = Organization(**defaults)
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        return org
    
    @staticmethod
    def create_user(db_session: Session, organization: Organization, **kwargs) -> User:
        """Create a test user with custom parameters."""
        defaults = {
            "email": "test@example.com",
            "hashed_password": get_password_hash("testpassword123"),
            "first_name": "Test",
            "last_name": "User",
            "role": "engineer",
            "organization_id": organization.id,
            "is_active": True,
            "is_verified": True
        }
        defaults.update(kwargs)
        
        user = User(**defaults)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock data for calculations
MOCK_CALCULATION_DATA = {
    "pressure_vessel": {
        "design_pressure": 150.0,
        "design_temperature": 350.0,
        "inside_diameter": 48.0,
        "wall_thickness": 0.25,
        "material_yield_strength": 38000.0,
        "joint_efficiency": 1.0,
        "corrosion_allowance": 0.125
    },
    "piping": {
        "design_pressure": 300.0,
        "design_temperature": 400.0,
        "nominal_diameter": 6.0,
        "wall_thickness": 0.280,
        "material_yield_strength": 35000.0,
        "temperature_derating_factor": 1.0
    }
}


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Set test environment
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = SQLALCHEMY_TEST_DATABASE_URL
    
    # Configure logging for tests
    import logging
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add markers based on test file location
        if "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "test_models" in str(item.fspath):
            item.add_marker(pytest.mark.models)
        elif "test_calculations" in str(item.fspath):
            item.add_marker(pytest.mark.calculations)
        elif "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
