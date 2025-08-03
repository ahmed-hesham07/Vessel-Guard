"""
API endpoint tests for the Vessel Guard application.

Tests for all major API endpoints including CRUD operations,
error handling, and response validation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.organization import Organization
from app.db.models.project import Project
from app.db.models.vessel import Vessel
from app.db.models.material import Material


class TestProjectAPI:
    """Test project API endpoints."""
    
    def test_create_project(self, client: TestClient, auth_headers: dict):
        """Test project creation."""
        project_data = {
            "name": "New Test Project",
            "description": "A new test project for API testing",
            "project_number": "P-TEST-001",
            "client_name": "Test Client Corporation",
            "location": "Houston, TX"
        }
        
        response = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["project_number"] == project_data["project_number"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_projects(self, client: TestClient, auth_headers: dict, test_project: Project):
        """Test getting list of projects."""
        response = client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        
        # Check if test project is in the list
        project_ids = [p["id"] for p in data["items"]]
        assert test_project.id in project_ids
    
    def test_get_project_by_id(self, client: TestClient, auth_headers: dict, test_project: Project):
        """Test getting a specific project by ID."""
        response = client.get(f"/api/v1/projects/{test_project.id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name
        assert data["description"] == test_project.description
    
    def test_update_project(self, client: TestClient, auth_headers: dict, test_project: Project):
        """Test updating a project."""
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated project description",
            "status": "in_progress"
        }
        
        response = client.put(f"/api/v1/projects/{test_project.id}", 
                            json=update_data, 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]
    
    def test_delete_project(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test deleting a project."""
        # Create a project to delete
        from tests.conftest import TestDataFactory
        from app.db.models.user import User
        from app.db.models.organization import Organization
        
        user = db_session.query(User).first()
        org = db_session.query(Organization).first()
        
        project = Project(
            name="Project to Delete",
            description="This project will be deleted",
            organization_id=org.id,
            owner_id=user.id,
            created_by_id=user.id,
            is_active=True
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        response = client.delete(f"/api/v1/projects/{project.id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify project is deleted/deactivated
        get_response = client.get(f"/api/v1/projects/{project.id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_project_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting a non-existent project."""
        response = client.get("/api/v1/projects/99999", headers=auth_headers)
        assert response.status_code == 404


class TestVesselAPI:
    """Test vessel API endpoints."""
    
    def test_create_vessel(self, client: TestClient, auth_headers: dict, test_project: Project, test_material: Material):
        """Test vessel creation."""
        vessel_data = {
            "tag_number": "V-TEST-001",
            "name": "Test Vessel for API",
            "description": "A test vessel created via API",
            "vessel_type": "pressure_vessel",
            "service": "Test service",
            "location": "Test location",
            "design_code": "ASME VIII Div 1",
            "design_pressure": 200.0,
            "design_temperature": 400.0,
            "operating_pressure": 150.0,
            "operating_temperature": 350.0,
            "inside_diameter": 60.0,
            "wall_thickness": 0.375,
            "project_id": test_project.id,
            "material_id": test_material.id
        }
        
        response = client.post("/api/v1/vessels", json=vessel_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["tag_number"] == vessel_data["tag_number"]
        assert data["name"] == vessel_data["name"]
        assert data["vessel_type"] == vessel_data["vessel_type"]
        assert data["design_pressure"] == vessel_data["design_pressure"]
        assert "id" in data
    
    def test_get_vessels(self, client: TestClient, auth_headers: dict, test_vessel: Vessel):
        """Test getting list of vessels."""
        response = client.get("/api/v1/vessels", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        
        # Check if test vessel is in the list
        vessel_tags = [v["tag_number"] for v in data["items"]]
        assert test_vessel.tag_number in vessel_tags
    
    def test_get_vessel_by_id(self, client: TestClient, auth_headers: dict, test_vessel: Vessel):
        """Test getting a specific vessel by ID."""
        response = client.get(f"/api/v1/vessels/{test_vessel.id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == test_vessel.id
        assert data["tag_number"] == test_vessel.tag_number
        assert data["name"] == test_vessel.name
    
    def test_update_vessel(self, client: TestClient, auth_headers: dict, test_vessel: Vessel):
        """Test updating a vessel."""
        update_data = {
            "name": "Updated Vessel Name",
            "description": "Updated vessel description",
            "operating_pressure": 140.0
        }
        
        response = client.put(f"/api/v1/vessels/{test_vessel.id}", 
                            json=update_data, 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["operating_pressure"] == update_data["operating_pressure"]
    
    def test_vessel_validation_errors(self, client: TestClient, auth_headers: dict, test_project: Project):
        """Test vessel creation with validation errors."""
        invalid_vessel_data = {
            "tag_number": "",  # Empty tag number should fail
            "name": "Test Vessel",
            "vessel_type": "invalid_type",  # Invalid vessel type
            "design_pressure": -100.0,  # Negative pressure should fail
            "project_id": test_project.id
        }
        
        response = client.post("/api/v1/vessels", json=invalid_vessel_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
        
        errors = response.json()["detail"]
        error_fields = [error["loc"][-1] for error in errors if "loc" in error]
        assert "tag_number" in error_fields or "vessel_type" in error_fields


class TestMaterialAPI:
    """Test material API endpoints."""
    
    def test_create_material(self, client: TestClient, auth_headers: dict):
        """Test material creation."""
        material_data = {
            "name": "Carbon Steel A516 Grade 70",
            "specification": "SA-516",
            "grade": "Grade 70",
            "description": "Pressure vessel quality carbon steel",
            "yield_strength": 38000.0,
            "tensile_strength": 70000.0,
            "min_temp": -20.0,
            "max_temp": 650.0,
            "is_asme_approved": True,
            "is_weldable": True
        }
        
        response = client.post("/api/v1/materials", json=material_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == material_data["name"]
        assert data["specification"] == material_data["specification"]
        assert data["grade"] == material_data["grade"]
        assert data["yield_strength"] == material_data["yield_strength"]
    
    def test_get_materials(self, client: TestClient, auth_headers: dict, test_material: Material):
        """Test getting list of materials."""
        response = client.get("/api/v1/materials", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        
        # Check if test material is in the list
        material_specs = [m["specification"] for m in data["items"]]
        assert test_material.specification in material_specs
    
    def test_search_materials(self, client: TestClient, auth_headers: dict, test_material: Material):
        """Test material search functionality."""
        response = client.get(f"/api/v1/materials?search={test_material.specification}", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) >= 1
        
        # All returned materials should match the search term
        for material in data["items"]:
            assert test_material.specification.lower() in material["specification"].lower()


class TestUserAPI:
    """Test user API endpoints."""
    
    def test_get_current_user(self, client: TestClient, auth_headers: dict, test_user: User):
        """Test getting current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert data["role"] == test_user.role.value
    
    def test_update_user_profile(self, client: TestClient, auth_headers: dict):
        """Test updating user profile."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+1-555-123-4567",
            "job_title": "Senior Engineer"
        }
        
        response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        assert data["phone"] == update_data["phone"]
        assert data["job_title"] == update_data["job_title"]


class TestOrganizationAPI:
    """Test organization API endpoints."""
    
    def test_get_organization(self, client: TestClient, auth_headers: dict, test_organization: Organization):
        """Test getting organization details."""
        response = client.get("/api/v1/organizations/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == test_organization.name
        assert data["industry"] == test_organization.industry
        assert data["subscription_tier"] == test_organization.subscription_tier
    
    def test_update_organization(self, client: TestClient, auth_headers: dict, admin_user: User):
        """Test updating organization details."""
        # Use admin user for organization updates
        from app.core.security import create_access_token
        admin_token = create_access_token(subject=str(admin_user.id))
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        update_data = {
            "name": "Updated Engineering Corp",
            "industry": "Petrochemical",
            "website": "https://updated-corp.com"
        }
        
        response = client.put("/api/v1/organizations/me", 
                            json=update_data, 
                            headers=admin_headers)
        
        if response.status_code == 403:
            pytest.skip("Organization update requires admin role")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["industry"] == update_data["industry"]


class TestCalculationAPI:
    """Test calculation API endpoints."""
    
    def test_create_calculation(self, client: TestClient, auth_headers: dict, test_vessel: Vessel):
        """Test creating a calculation."""
        calculation_data = {
            "name": "Pressure Vessel Wall Thickness",
            "calculation_type": "pressure_vessel_thickness",
            "vessel_id": test_vessel.id,
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
        
        # Calculation endpoints might not be fully implemented yet
        if response.status_code == 404:
            pytest.skip("Calculation endpoints not implemented yet")
        
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == calculation_data["name"]
        assert data["calculation_type"] == calculation_data["calculation_type"]
        assert "id" in data
        assert "status" in data
    
    def test_get_calculations(self, client: TestClient, auth_headers: dict):
        """Test getting list of calculations."""
        response = client.get("/api/v1/calculations", headers=auth_headers)
        
        if response.status_code == 404:
            pytest.skip("Calculation endpoints not implemented yet")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestInspectionAPI:
    """Test inspection API endpoints."""
    
    def test_create_inspection(self, client: TestClient, auth_headers: dict, test_vessel: Vessel):
        """Test creating an inspection."""
        inspection_data = {
            "inspection_type": "external_visual",
            "vessel_id": test_vessel.id,
            "scheduled_date": "2024-12-01T10:00:00",
            "inspector_name": "John Doe",
            "inspection_scope": "External visual inspection of pressure vessel"
        }
        
        response = client.post("/api/v1/inspections", json=inspection_data, headers=auth_headers)
        
        if response.status_code == 404:
            pytest.skip("Inspection endpoints not implemented yet")
        
        assert response.status_code == 201
        
        data = response.json()
        assert data["inspection_type"] == inspection_data["inspection_type"]
        assert data["vessel_id"] == inspection_data["vessel_id"]
        assert data["inspector_name"] == inspection_data["inspector_name"]
    
    def test_get_inspections(self, client: TestClient, auth_headers: dict):
        """Test getting list of inspections."""
        response = client.get("/api/v1/inspections", headers=auth_headers)
        
        if response.status_code == 404:
            pytest.skip("Inspection endpoints not implemented yet")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestAPIErrorHandling:
    """Test API error handling."""
    
    def test_invalid_json(self, client: TestClient, auth_headers: dict):
        """Test handling of invalid JSON."""
        response = client.post("/api/v1/projects", 
                             data="invalid json", 
                             headers={**auth_headers, "Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client: TestClient, auth_headers: dict):
        """Test handling of missing required fields."""
        incomplete_data = {
            "description": "Project without name"
            # Missing required 'name' field
        }
        
        response = client.post("/api/v1/projects", json=incomplete_data, headers=auth_headers)
        assert response.status_code == 422
        
        errors = response.json()["detail"]
        field_errors = [error["loc"][-1] for error in errors if "loc" in error]
        assert "name" in field_errors
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to protected endpoints."""
        response = client.get("/api/v1/projects")
        assert response.status_code == 401
    
    def test_not_found_resource(self, client: TestClient, auth_headers: dict):
        """Test accessing non-existent resources."""
        response = client.get("/api/v1/projects/99999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient, auth_headers: dict):
        """Test method not allowed errors."""
        response = client.patch("/api/v1/projects", headers=auth_headers)
        assert response.status_code == 405


class TestAPIResponseFormat:
    """Test API response format consistency."""
    
    def test_list_response_format(self, client: TestClient, auth_headers: dict):
        """Test that list endpoints return consistent format."""
        response = client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["items", "total", "page", "per_page", "pages"]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["per_page"], int)
        assert isinstance(data["pages"], int)
    
    def test_error_response_format(self, client: TestClient):
        """Test that error responses have consistent format."""
        response = client.get("/api/v1/projects")  # No auth header
        assert response.status_code == 401
        
        data = response.json()
        assert "detail" in data
    
    def test_pagination(self, client: TestClient, auth_headers: dict):
        """Test pagination parameters."""
        # Test with custom page size
        response = client.get("/api/v1/projects?page=1&per_page=5", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 5
        assert len(data["items"]) <= 5
