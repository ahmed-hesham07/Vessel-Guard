"""
Authentication service for handling login, token management, and security.

This service provides methods for user authentication, JWT token creation,
password reset, and session management.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError

from app.db.models.user import User
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.core.exceptions import ValidationError, AuthenticationError
from app.services.user_service import UserService


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.user_service.get_user_by_email(email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def create_access_token(self, user_id: int, organization_id: int, 
                          expires_delta: Optional[timedelta] = None) -> Dict[str, Any]:
        """Create JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "user_id": user_id,
            "organization_id": organization_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": int(expires_delta.total_seconds()) if expires_delta else self.access_token_expire_minutes * 60,
            "expires_at": expire.isoformat()
        }
    
    def create_refresh_token(self, user_id: int, organization_id: int) -> str:
        """Create JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last 7 days
        
        to_encode = {
            "user_id": user_id,
            "organization_id": organization_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token has expired
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                return None
            
            return payload
        except PyJWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = self.user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("user_id")
        organization_id = payload.get("organization_id")
        
        if not user_id or not organization_id:
            return None
        
        # Verify user still exists and is active
        user = self.user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        # Create new access token
        return self.create_access_token(user_id, organization_id)
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Complete login process."""
        user = self.authenticate_user(email, password)
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        # Create tokens
        access_token_data = self.create_access_token(user.id, user.organization_id)
        refresh_token = self.create_refresh_token(user.id, user.organization_id)
        
        # Update last login time
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        return {
            "access_token": access_token_data["access_token"],
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": access_token_data["expires_in"],
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "organization_id": user.organization_id
            }
        }
    
    def logout(self, token: str) -> bool:
        """Logout user (invalidate token)."""
        # In a production system, you might want to maintain a blacklist of tokens
        # For now, we'll just verify the token is valid
        payload = self.verify_token(token)
        return payload is not None
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password with current password verification."""
        return self.user_service.change_password(user_id, current_password, new_password)
    
    def generate_password_reset_token(self, email: str) -> Optional[str]:
        """Generate password reset token."""
        user = self.user_service.get_user_by_email(email)
        if not user:
            return None
        
        expire = datetime.utcnow() + timedelta(hours=1)  # Reset tokens expire in 1 hour
        
        to_encode = {
            "user_id": user.id,
            "email": user.email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "password_reset"
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_password_reset_token(self, token: str) -> Optional[int]:
        """Verify password reset token and return user ID."""
        payload = self.verify_token(token)
        if not payload or payload.get("type") != "password_reset":
            return None
        
        return payload.get("user_id")
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using reset token."""
        user_id = self.verify_password_reset_token(token)
        if not user_id:
            raise ValidationError("Invalid or expired reset token")
        
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        return True
    
    def generate_email_verification_token(self, user_id: int) -> str:
        """Generate email verification token."""
        expire = datetime.utcnow() + timedelta(days=1)  # Verification tokens expire in 1 day
        
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "email_verification"
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_email_token(self, token: str) -> bool:
        """Verify email using verification token."""
        payload = self.verify_token(token)
        if not payload or payload.get("type") != "email_verification":
            return False
        
        user_id = payload.get("user_id")
        if not user_id:
            return False
        
        user = self.user_service.verify_user_email(user_id)
        return user is not None
    
    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """Check password strength and return analysis."""
        import re
        
        checks = {
            "length": len(password) >= 8,
            "uppercase": bool(re.search(r'[A-Z]', password)),
            "lowercase": bool(re.search(r'[a-z]', password)),
            "digit": bool(re.search(r'\d', password)),
            "special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }
        
        score = sum(checks.values())
        
        if score == 5:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            "strength": strength,
            "score": score,
            "max_score": 5,
            "checks": checks,
            "suggestions": self._get_password_suggestions(checks)
        }
    
    def _get_password_suggestions(self, checks: Dict[str, bool]) -> list:
        """Get password improvement suggestions."""
        suggestions = []
        
        if not checks["length"]:
            suggestions.append("Use at least 8 characters")
        if not checks["uppercase"]:
            suggestions.append("Include at least one uppercase letter")
        if not checks["lowercase"]:
            suggestions.append("Include at least one lowercase letter")
        if not checks["digit"]:
            suggestions.append("Include at least one number")
        if not checks["special"]:
            suggestions.append("Include at least one special character (!@#$%^&*)")
        
        return suggestions
    
    def get_user_sessions(self, user_id: int) -> Dict[str, Any]:
        """Get active sessions for a user (mock implementation)."""
        # In a production system, you would track active sessions
        # This is a placeholder implementation
        return {
            "active_sessions": 1,
            "last_login": datetime.utcnow().isoformat(),
            "login_count": 1
        }
    
    def revoke_all_sessions(self, user_id: int) -> bool:
        """Revoke all sessions for a user (mock implementation)."""
        # In a production system, you would invalidate all tokens for the user
        # This could be done by updating a token version number or maintaining a blacklist
        return True
