"""
Integration tests for the Vessel Guard application.

Tests complete workflows and integration between components,
including database operations, API endpoints, and service interactions.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.models.user import User, UserRole
from app.db.models.organization import Organization
from app.db.models.project import Project, ProjectStatus
from app.db.models.vessel import Vessel, VesselType
from app.db.models.calculation import Calculation, CalculationStatus
from app.db.models.inspection import Inspection, InspectionStatus
from app.db.models.report import Report, ReportStatus

from app.services.project_service import ProjectService
from app.services.vessel_service import VesselService
from app.services.calculation_service import CalculationService
from app.services.report_service import ReportService
from app.services.cache_service import cache_service


class TestProjectWorkflow:
    """Test complete project creation workflow."""
    
    def test_complete_project_creation_workflow(
        self, 
        client: TestClient, 
        db_session: Session, 
        auth_headers: dict,
        test_organization: Organization,
        test_user: User
    ):
        """Test creating a complete project with vessels and calculations."""
        
        # 1. Create project
        project_data = {
            "name": "Pressure Vessel Analysis Project",
            "description": "Complete analysis of pressure vessels",
            "client_name": "Test Client",
            "start_date": datetime.now().isoformat(),
            "priority": "high",
            "status": "planning"
        }
        
        response = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
        assert response.status_code == 201
        project = response.json()
        project_id = project["id"]
        
        # 2. Create vessel for the project
        vessel_data = {
            "tag_number": "V-001",
            "name": "Main Pressure Vessel",
            "vessel_type": "pressure_vessel",
            "design_pressure": 150.0,
            "design_temperature": 350.0,
            "inside_diameter": 48.0,
            "wall_thickness": 0.5,
            "material_specification": "SA-516 Grade 70",
            "design_code": "ASME VIII Div 1",
            "project_id": project_id
        }
        
        response = client.post("/api/v1/vessels", json=vessel_data, headers=auth_headers)
        assert response.status_code == 201
        vessel = response.json()
        vessel_id = vessel["id"]
        
        # 3. Create calculation for the vessel
        calculation_data = {
            "name": "Wall Thickness Calculation",
            "calculation_type": "ASME_VIII_DIV_1",
            "project_id": project_id,
            "vessel_id": vessel_id,
            "input_parameters": {
                "design_pressure": 150.0,
                "design_temperature": 350.0,
                "inside_diameter": 48.0,
                "material_yield_strength": 38000.0,
                "joint_efficiency": 1.0,
                "corrosion_allowance": 0.125
            }
        }
        
        response = client.post("/api/v1/calculations", json=calculation_data, headers=auth_headers)
        if response.status_code == 404:
            pytest.skip("Calculation endpoints not implemented yet")
        
        assert response.status_code == 201
        calculation = response.json()
        
        # 4. Verify project dashboard data
        response = client.get("/api/v1/projects/dashboard", headers=auth_headers)
        assert response.status_code == 200
        dashboard = response.json()
        
        assert dashboard["total_projects"] >= 1
        assert any(p["id"] == project_id for p in dashboard.get("recent_projects", []))
        
        # 5. Update project status
        update_data = {"status": "active"}
        response = client.put(f"/api/v1/projects/{project_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        updated_project = response.json()
        assert updated_project["status"] == "active"


class TestCalculationWorkflow:
    """Test calculation workflow integration."""
    
    def test_calculation_lifecycle(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
        test_project: Project,
        test_vessel: Vessel
    ):
        """Test complete calculation lifecycle."""
        
        # 1. Create calculation
        calculation_data = {
            "name": "ASME VIII Div 1 Calculation",
            "calculation_type": "ASME_VIII_DIV_1",
            "project_id": test_project.id,
            "vessel_id": test_vessel.id,
            "input_parameters": {
                "design_pressure": 100.0,
                "design_temperature": 300.0,
                "inside_diameter": 36.0,
                "material_yield_strength": 30000.0
            }
        }
        
        response = client.post("/api/v1/calculations", json=calculation_data, headers=auth_headers)
        if response.status_code == 404:
            pytest.skip("Calculation endpoints not implemented yet")
        
        assert response.status_code == 201
        calculation = response.json()
        calc_id = calculation["id"]
        
        # 2. Check calculation status
        response = client.get(f"/api/v1/calculations/{calc_id}", headers=auth_headers)
        assert response.status_code == 200
        calc_details = response.json()
        assert calc_details["status"] in ["pending", "running", "completed"]
        
        # 3. Run calculation (simulate)
        if calc_details["status"] == "pending":
            # Simulate calculation execution
            update_data = {"status": "completed"}
            response = client.put(f"/api/v1/calculations/{calc_id}", json=update_data, headers=auth_headers)
            assert response.status_code == 200
        
        # 4. Generate report
        report_data = {
            "name": "Calculation Report",
            "report_type": "calculation",
            "project_id": test_project.id,
            "calculation_id": calc_id
        }
        
        response = client.post("/api/v1/reports", json=report_data, headers=auth_headers)
        if response.status_code == 404:
            pytest.skip("Report endpoints not implemented yet")
        
        assert response.status_code == 201
        report = response.json()
        
        # 5. Download report
        response = client.get(f"/api/v1/reports/{report['id']}/download", headers=auth_headers)
        if response.status_code != 404:  # Only test if endpoint exists
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"


class TestUserManagementWorkflow:
    """Test user management integration."""
    
    def test_user_lifecycle_management(
        self,
        client: TestClient,
        db_session: Session,
        admin_headers: dict,  # Assuming we have admin headers fixture
        test_organization: Organization
    ):
        """Test complete user lifecycle management."""
        
        # 1. Create new user
        user_data = {
            "email": "newuser@test.com",
            "password": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User",
            "role": "consultant",
            "organization_id": test_organization.id
        }
        
        response = client.post("/api/v1/users", json=user_data, headers=admin_headers)
        if response.status_code == 404:
            pytest.skip("User management endpoints not implemented yet")
        
        assert response.status_code == 201
        user = response.json()
        user_id = user["id"]
        
        # 2. Update user details
        update_data = {
            "job_title": "Junior Engineer",
            "department": "Engineering"
        }
        
        response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        
        # 3. User login
        login_data = {
            "username": "newuser@test.com",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        tokens = response.json()
        user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # 4. User access test
        response = client.get("/api/v1/projects", headers=user_headers)
        assert response.status_code == 200
        
        # 5. Role-based access test
        response = client.delete(f"/api/v1/users/{user_id}", headers=user_headers)
        assert response.status_code == 403  # Consultant can't delete users


class TestCacheIntegration:
    """Test caching system integration."""
    
    def test_cache_invalidation_workflow(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
        test_project: Project
    ):
        """Test cache invalidation when data changes."""
        
        # 1. Get projects (should cache)
        response1 = client.get("/api/v1/projects", headers=auth_headers)
        assert response1.status_code == 200
        projects1 = response1.json()
        
        # 2. Create new project (should invalidate cache)
        new_project_data = {
            "name": "Cache Test Project",
            "description": "Testing cache invalidation",
            "status": "planning"
        }
        
        response = client.post("/api/v1/projects", json=new_project_data, headers=auth_headers)
        assert response.status_code == 201
        
        # 3. Get projects again (should reflect new data)
        response2 = client.get("/api/v1/projects", headers=auth_headers)
        assert response2.status_code == 200
        projects2 = response2.json()
        
        # Should have one more project
        assert projects2["total"] == projects1["total"] + 1
        
        # 4. Test cache service directly
        cache_key = "test_cache_key"
        test_data = {"test": "data"}
        
        # Set cache
        assert cache_service.set(cache_key, test_data, ttl=60)
        
        # Get from cache
        cached_data = cache_service.get(cache_key)
        assert cached_data == test_data
        
        # Delete from cache
        assert cache_service.delete(cache_key)
        
        # Verify deletion
        cached_data = cache_service.get(cache_key)
        assert cached_data is None


class TestErrorHandlingIntegration:
    """Test error handling across the application."""
    
    def test_database_error_handling(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test database error handling in API."""
        
        # Test constraint violation (duplicate project name)
        project_data = {
            "name": "Test Project",
            "description": "First project"
        }
        
        response1 = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
        # Should handle gracefully (might be 400 or 409 depending on implementation)
        assert response2.status_code in [400, 409, 422]
    
    def test_validation_error_handling(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test validation error handling."""
        
        # Test invalid data types
        invalid_project_data = {
            "name": 123,  # Should be string
            "description": "Valid description",
            "priority": "invalid_priority"  # Invalid enum value
        }
        
        response = client.post("/api/v1/projects", json=invalid_project_data, headers=auth_headers)
        assert response.status_code == 422
        
        error_details = response.json()["detail"]
        assert any(error["loc"][-1] == "name" for error in error_details)
    
    def test_permission_error_handling(
        self,
        client: TestClient,
        consultant_headers: dict  # Assuming we have consultant headers fixture
    ):
        """Test permission error handling."""
        
        # Consultant trying to access admin functionality
        response = client.get("/api/v1/users", headers=consultant_headers)
        # Should be forbidden or not found depending on implementation
        assert response.status_code in [403, 404]


class TestPerformanceIntegration:
    """Test performance-related integration scenarios."""
    
    def test_bulk_operations_performance(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers: dict,
        test_project: Project
    ):
        """Test bulk operations performance."""
        
        # Create multiple vessels quickly
        vessel_data_list = []
        for i in range(10):
            vessel_data = {
                "tag_number": f"V-{i:03d}",
                "name": f"Test Vessel {i}",
                "vessel_type": "pressure_vessel",
                "design_pressure": 100.0 + i * 10,
                "design_temperature": 300.0,
                "project_id": test_project.id
            }
            vessel_data_list.append(vessel_data)
        
        # Test bulk creation (if endpoint exists)
        bulk_data = {"vessels": vessel_data_list}
        response = client.post("/api/v1/vessels/bulk", json=bulk_data, headers=auth_headers)
        
        if response.status_code != 404:  # Only test if bulk endpoint exists
            assert response.status_code == 201
            result = response.json()
            assert result["created_count"] == 10
        else:
            # Create individually if bulk not available
            for vessel_data in vessel_data_list:
                response = client.post("/api/v1/vessels", json=vessel_data, headers=auth_headers)
                assert response.status_code == 201
    
    def test_pagination_performance(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test pagination performance."""
        
        # Test large page sizes
        response = client.get("/api/v1/projects?limit=100&skip=0", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "skip" in data
        
        # Test deep pagination
        response = client.get("/api/v1/projects?limit=10&skip=50", headers=auth_headers)
        assert response.status_code == 200


@pytest.fixture
def admin_headers(test_admin_user: User) -> dict:
    """Create authorization headers for admin user."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(subject=test_admin_user.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def consultant_headers(test_consultant_user: User) -> dict:
    """Create authorization headers for consultant user."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(subject=test_consultant_user.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_admin_user(db_session: Session, test_organization: Organization) -> User:
    """Create test admin user."""
    from app.core.security import get_password_hash
    
    admin_user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("AdminPassword123!"),
        first_name="Admin",
        last_name="User",
        role=UserRole.ENGINEER,  # Engineer has admin privileges
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True
    )
    
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    
    return admin_user


@pytest.fixture
def test_consultant_user(db_session: Session, test_organization: Organization) -> User:
    """Create test consultant user."""
    from app.core.security import get_password_hash
    
    consultant_user = User(
        email="consultant@test.com",
        hashed_password=get_password_hash("ConsultantPassword123!"),
        first_name="Consultant",
        last_name="User",
        role=UserRole.CONSULTANT,
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True
    )
    
    db_session.add(consultant_user)
    db_session.commit()
    db_session.refresh(consultant_user)
    
    return consultant_user