"""
Authentication endpoints for user login, registration, and token management.

Provides JWT-based authentication with secure token handling
and user account management.
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token,
    validate_password_strength,
    generate_password_reset_token,
    verify_password_reset_token
)
from app.crud.user import user_crud
from app.db.models.user import User
from app.schemas.auth import (
    Token,
    TokenRefresh,
    UserLogin,
    UserRegister,
    PasswordReset,
    PasswordResetRequest,
    AuthResponse
)
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, Any]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, 
        expires_delta=access_token_expires,
        additional_claims={"role": user.role, "org_id": user.organization_id}
    )
    
    refresh_token = create_refresh_token(subject=user.id)
    
    # Update last login
    user_crud.update_last_login(db, user=user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserResponse.from_orm(user)
    }


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> User:
    """
    Register a new user account.
    """
    # Check if user already exists
    existing_user = user_crud.get_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    password_validation = validate_password_strength(user_data.password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
        )
    
    # Get default organization (or create if none exists)
    from app.db.models.organization import Organization
    default_org = db.query(Organization).first()
    if not default_org:
        default_org = Organization(
            name="Default Organization",
            description="Default organization for Vessel Guard",
            subscription_type="trial",
            is_active=True
        )
        db.add(default_org)
        db.commit()
        db.refresh(default_org)
    
    # Handle organization creation if user provided organization_name
    if user_data.organization_name:
        # Check if organization exists
        org = db.query(Organization).filter(
            Organization.name == user_data.organization_name
        ).first()
        if not org:
            org = Organization(
                name=user_data.organization_name,
                description=f"Organization for {user_data.organization_name}",
                subscription_type="trial",
                is_active=True
            )
            db.add(org)
            db.commit()
            db.refresh(org)
        organization_id = org.id
    else:
        organization_id = default_org.id
    
    # Convert UserRegister to UserCreate with proper fields
    from app.schemas.user import UserCreate
    from app.db.models.user import UserRole
    
    user_create_data = UserCreate(
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        job_title=user_data.job_title,
        department=user_data.department,
        role=UserRole.VIEWER,  # Default role for new users
        timezone="UTC",  # Default timezone
        language="en",  # Default language
        organization_id=organization_id
    )
    
    # Create user
    user = user_crud.create(db, obj_in=user_create_data)
    
    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    """
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = user_crud.get(db, id=int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={"role": user.role, "org_id": user.organization_id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Logout current user (token invalidation would be handled by client).
    """
    # In a production system, you would add the token to a blacklist
    # For now, we just return success
    return {"message": "Successfully logged out"}


@router.post("/password-reset/request")
async def request_password_reset(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Request password reset token.
    """
    user = user_crud.get_by_email(db, email=request_data.email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate password reset token
    reset_token = generate_password_reset_token(user.email)
    
    # In production, send email with reset token
    # For now, we'll just store it (in real app, send via email service)
    user_crud.set_password_reset_token(db, user=user, token=reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Confirm password reset with token.
    """
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
    
    user = user_crud.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate new password
    password_validation = validate_password_strength(reset_data.new_password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
        )
    
    # Update password
    hashed_password = get_password_hash(reset_data.new_password)
    user_crud.update_password(db, user=user, hashed_password=hashed_password)
    
    # Clear reset token
    user_crud.clear_password_reset_token(db, user=user)
    
    return {"message": "Password successfully reset"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user information.
    """
    return current_user


@router.post("/verify-token")
async def verify_access_token(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify if current access token is valid.
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "organization_id": current_user.organization_id
    }
