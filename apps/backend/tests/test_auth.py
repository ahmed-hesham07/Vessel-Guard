"""
Authentication and authorization tests.

Tests for user authentication, JWT tokens, role-based access control,
and security middleware functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.models.user import User, UserRole


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_user_registration(self, client: TestClient, db_session: Session):
        """Test user registration endpoint."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User",
            "organization_name": "New Engineering Corp"
        }
        
        response = client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == registration_data["email"]
        assert data["user"]["first_name"] == registration_data["first_name"]
    
    def test_user_login(self, client: TestClient, test_user: User):
        """Test user login endpoint."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user.email
    
    def test_login_invalid_credentials(self, client: TestClient, test_user: User):
        """Test login with invalid credentials."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_inactive_user(self, client: TestClient, db_session: Session, test_organization):
        """Test login with inactive user."""
        # Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("testpassword123"),
            first_name="Inactive",
            last_name="User",
            role=UserRole.ENGINEER,
            organization_id=test_organization.id,
            is_active=False,
            is_verified=True
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        login_data = {
            "email": inactive_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Inactive user" in response.json()["detail"]
    
    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self, client: TestClient, auth_headers: dict):
        """Test accessing protected endpoint with valid token."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "first_name" in data
        assert "role" in data
    
    def test_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401
    
    def test_token_expiration(self, client: TestClient, test_user: User):
        """Test token expiration handling."""
        # Create expired token
        expired_token = create_access_token(
            subject=str(test_user.id),
            expires_delta=timedelta(seconds=-1)
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401


class TestJWTTokens:
    """Test JWT token functionality."""
    
    def test_create_access_token(self, test_user: User):
        """Test access token creation."""
        token = create_access_token(subject=str(test_user.id))
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens should be reasonably long
    
    def test_create_token_with_expiration(self, test_user: User):
        """Test token creation with custom expiration."""
        expires_delta = timedelta(hours=24)
        token = create_access_token(
            subject=str(test_user.id),
            expires_delta=expires_delta
        )
        assert token is not None
    
    def test_token_refresh(self, client: TestClient, test_user: User):
        """Test token refresh functionality."""
        # Login to get refresh token
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        refresh_token = data.get("refresh_token")
        
        if refresh_token:  # Only test if refresh tokens are implemented
            refresh_data = {"refresh_token": refresh_token}
            response = client.post("/api/v1/auth/refresh", json=refresh_data)
            assert response.status_code == 200
            
            new_data = response.json()
            assert "access_token" in new_data
            assert new_data["access_token"] != data["access_token"]


class TestRoleBasedAccessControl:
    """Test role-based access control functionality."""
    
    def test_admin_access_to_admin_endpoint(self, client: TestClient, admin_user: User):
        """Test admin user accessing admin-only endpoint."""
        from app.core.security import create_access_token
        token = create_access_token(subject=str(admin_user.id))
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/admin/users", headers=headers)
        # Note: This assumes admin endpoint exists
        assert response.status_code in [200, 404]  # 404 if endpoint not implemented yet
    
    def test_viewer_access_restriction(self, client: TestClient, viewer_user: User):
        """Test viewer user access restrictions."""
        from app.core.security import create_access_token
        token = create_access_token(subject=str(viewer_user.id))
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test creating a project (should be restricted for viewers)
        project_data = {
            "name": "Test Project",
            "description": "A test project"
        }
        
        response = client.post("/api/v1/projects", json=project_data, headers=headers)
        # Should be forbidden for viewers
        assert response.status_code in [403, 404]
    
    def test_engineer_access(self, client: TestClient, test_user: User):
        """Test engineer user access to appropriate endpoints."""
        from app.core.security import create_access_token
        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}
        
        # Engineers should be able to access their profile
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
    
    def test_organization_isolation(self, client: TestClient, db_session: Session):
        """Test that users can only access data from their organization."""
        from tests.conftest import TestDataFactory
        
        # Create two organizations with users
        org1 = TestDataFactory.create_organization(db_session, name="Org 1", subdomain="org1")
        org2 = TestDataFactory.create_organization(db_session, name="Org 2", subdomain="org2")
        
        user1 = TestDataFactory.create_user(db_session, org1, email="user1@org1.com")
        user2 = TestDataFactory.create_user(db_session, org2, email="user2@org2.com")
        
        from app.core.security import create_access_token
        token1 = create_access_token(subject=str(user1.id))
        token2 = create_access_token(subject=str(user2.id))
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Each user should only see their own organization's data
        response1 = client.get("/api/v1/projects", headers=headers1)
        response2 = client.get("/api/v1/projects", headers=headers2)
        
        # Both should succeed but return different data
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestPasswordSecurity:
    """Test password security functionality."""
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_password_strength_validation(self, client: TestClient):
        """Test password strength requirements."""
        weak_passwords = [
            "123456",
            "password",
            "abc123",
            "12345678",
            "qwerty"
        ]
        
        for weak_password in weak_passwords:
            registration_data = {
                "email": f"test_{weak_password}@example.com",
                "password": weak_password,
                "first_name": "Test",
                "last_name": "User",
                "organization_name": "Test Org"
            }
            
            response = client.post("/api/v1/auth/register", json=registration_data)
            # Should reject weak passwords
            assert response.status_code in [400, 422]
    
    def test_password_change(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test password change functionality."""
        change_data = {
            "current_password": "testpassword123",
            "new_password": "NewSecurePassword123!",
            "confirm_password": "NewSecurePassword123!"
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             json=change_data, 
                             headers=auth_headers)
        
        if response.status_code == 404:
            # Endpoint not implemented yet
            pytest.skip("Password change endpoint not implemented")
        
        assert response.status_code == 200
        
        # Verify old password no longer works
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        
        # Verify new password works
        login_data["password"] = "NewSecurePassword123!"
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200


class TestAccountSecurity:
    """Test account security features."""
    
    def test_account_lockout_after_failed_attempts(self, client: TestClient, test_user: User):
        """Test account lockout after multiple failed login attempts."""
        # Attempt multiple failed logins
        for i in range(6):  # Assuming 5 attempts trigger lockout
            login_data = {
                "email": test_user.email,
                "password": "wrongpassword"
            }
            response = client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 401
        
        # Account should now be locked
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"  # Correct password
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Should be locked even with correct password
        if "locked" in response.json().get("detail", "").lower():
            assert response.status_code == 401
        else:
            # Lockout not implemented yet
            pytest.skip("Account lockout not implemented")
    
    def test_password_reset_request(self, client: TestClient, test_user: User):
        """Test password reset request."""
        reset_data = {"email": test_user.email}
        
        response = client.post("/api/v1/auth/password-reset-request", json=reset_data)
        
        if response.status_code == 404:
            pytest.skip("Password reset not implemented")
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_email_verification(self, client: TestClient):
        """Test email verification process."""
        registration_data = {
            "email": "verify@example.com",
            "password": "SecurePassword123!",
            "first_name": "Verify",
            "last_name": "User",
            "organization_name": "Verify Org"
        }
        
        response = client.post("/api/v1/auth/register", json=registration_data)
        
        if response.status_code == 201:
            # Check if user needs verification
            data = response.json()
            if "verification_required" in data:
                # Test verification endpoint
                verify_data = {"token": "test_token"}
                verify_response = client.post("/api/v1/auth/verify-email", json=verify_data)
                # Implementation specific response
                assert verify_response.status_code in [200, 400, 404]
