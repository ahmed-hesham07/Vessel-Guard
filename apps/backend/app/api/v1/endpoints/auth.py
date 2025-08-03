"""
Authentication endpoints for user login, registration, and token management.

Provides JWT-based authentication with secure token handling
and user account management.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import ipaddress

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.services.audit_service import (
    audit_service, 
    AuditEventType, 
    AuditSeverity, 
    AuditContext
)
from app.middleware.enhanced_security import (
    validate_password_strength,
    threat_detector
)

logger = logging.getLogger(__name__)

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
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, Any]:
    """
    Enhanced OAuth2 compatible token login with security features.
    
    Includes audit logging, account lockout protection, and threat detection.
    """
    client_ip = _get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    
    # Create audit context
    audit_context = AuditContext(
        ip_address=client_ip,
        user_agent=user_agent,
        api_endpoint="/api/v1/auth/login",
        http_method="POST"
    )
    
    # Check if IP is blocked due to too many failed attempts
    if threat_detector.is_ip_blocked(client_ip):
        # Log blocked attempt
        audit_service.log_security_event(
            db=db,
            event_type=AuditEventType.BRUTE_FORCE_ATTEMPT,
            description=f"Login attempt from blocked IP: {client_ip}",
            context=audit_context,
            threat_details={"reason": "IP blocked due to repeated failures"},
            severity=AuditSeverity.HIGH
        )
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later.",
        )
    
    # Attempt authentication
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    # Handle failed authentication
    if not user:
        # Record failed login attempt
        threat_detector.record_failed_login(client_ip)
        
        # Log failed login attempt
        audit_service.log_authentication_event(
            db=db,
            event_type=AuditEventType.LOGIN_FAILURE,
            user_id=None,
            email=form_data.username,
            success=False,
            context=audit_context,
            failure_reason="Invalid credentials"
        )
        
        # Check for brute force pattern
        failure_count = len(threat_detector.failed_logins.get(client_ip, []))
        if failure_count >= 3:
            # Log potential brute force attempt
            audit_service.log_security_event(
                db=db,
                event_type=AuditEventType.BRUTE_FORCE_ATTEMPT,
                description=f"Multiple failed login attempts from {client_ip}",
                context=audit_context,
                threat_details={
                    "failure_count": failure_count,
                    "attempted_email": form_data.username
                },
                severity=AuditSeverity.HIGH
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user account is locked
    if hasattr(user, 'locked_until') and user.locked_until:
        if user.locked_until > datetime.now(timezone.utc):
            # Log locked account attempt
            audit_service.log_authentication_event(
                db=db,
                event_type=AuditEventType.LOGIN_FAILURE,
                user_id=user.id,
                email=user.email,
                success=False,
                context=audit_context,
                failure_reason="Account locked"
            )
            
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked. Please try again later.",
            )
        else:
            # Unlock account if lock period has expired
            user.locked_until = None
            user.failed_login_attempts = 0
            db.commit()
    
    # Check if user is active
    if not user.is_active:
        # Log inactive user attempt
        audit_service.log_authentication_event(
            db=db,
            event_type=AuditEventType.LOGIN_FAILURE,
            user_id=user.id,
            email=user.email,
            success=False,
            context=audit_context,
            failure_reason="Account inactive"
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive. Please contact support."
        )
    
    # Check for suspicious login patterns
    _check_suspicious_login(request, user, audit_context, db)
    
    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, 
        expires_delta=access_token_expires,
        additional_claims={
            "role": user.role, 
            "org_id": user.organization_id,
            "ip": client_ip
        }
    )
    
    refresh_token = create_refresh_token(subject=user.id)
    
    # Update last login and audit context
    audit_context.user_id = user.id
    audit_context.organization_id = user.organization_id
    
    # Update user last login
    user_crud.update_last_login(db, user=user)
    
    # Log successful login
    audit_service.log_authentication_event(
        db=db,
        event_type=AuditEventType.LOGIN_SUCCESS,
        user_id=user.id,
        email=user.email,
        success=True,
        context=audit_context
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserResponse.from_orm(user)
    }


def _get_client_ip(request: Request) -> str:
    """Get the real client IP address from request."""
    # Check for forwarded headers
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    if hasattr(request.client, "host"):
        return request.client.host
    
    return "unknown"


def _check_suspicious_login(request: Request, user: User, audit_context: AuditContext, db: Session):
    """Check for suspicious login patterns."""
    # Check for login from new location (simplified)
    client_ip = audit_context.ip_address
    
    # In production, you would check against user's historical IP ranges
    # For now, we'll just log if it's a significantly different IP range
    try:
        if client_ip and client_ip != "unknown":
            # Simple check for private vs public IP changes
            current_ip = ipaddress.ip_address(client_ip)
            if user.last_login:
                # You would store and compare with historical IPs
                # For now, just log the login for analysis
                audit_service.log_event(
                    db=db,
                    event_type=AuditEventType.LOGIN_SUCCESS,
                    description=f"Login from IP: {client_ip}",
                    context=audit_context,
                    severity=AuditSeverity.LOW,
                    details={
                        "new_ip": client_ip,
                        "ip_type": "private" if current_ip.is_private else "public"
                    }
                )
    except Exception:
        # If IP parsing fails, just continue
        pass


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Register a new user account.
    """
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    try:
        # Check if user already exists
        logger.debug("Checking if user already exists...")
        existing_user = user_crud.get_by_email(db, email=user_data.email)
        if existing_user:
            logger.warning(f"Registration failed - email already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        logger.debug("Validating password strength...")
        password_validation = validate_password_strength(user_data.password)
        if not password_validation["valid"]:
            logger.warning(f"Registration failed - password validation failed for: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
            )
        
        # Get default organization (or create if none exists)
        logger.debug("Handling organization setup...")
        from app.db.models.organization import Organization
        from app.db.models.organization import SubscriptionType
        
        try:
            default_org = db.query(Organization).first()
            if not default_org:
                logger.info("Creating default organization...")
                default_org = Organization(
                    name="Default Organization",
                    description="Default organization for Vessel Guard",
                    subscription_type=SubscriptionType.TRIAL,
                    is_active=True
                )
                db.add(default_org)
                db.commit()
                db.refresh(default_org)
                logger.info(f"Default organization created with ID: {default_org.id}")
        except Exception as e:
            logger.error(f"Failed to create default organization: {str(e)}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create default organization: {str(e)}"
            )
        
        # Handle organization creation if user provided organization_name
        organization_id = default_org.id
        if user_data.organization_name:
            logger.debug(f"Creating/finding organization: {user_data.organization_name}")
            try:
                # Check if organization exists
                org = db.query(Organization).filter(
                    Organization.name == user_data.organization_name
                ).first()
                if not org:
                    logger.info(f"Creating new organization: {user_data.organization_name}")
                    org = Organization(
                        name=user_data.organization_name,
                        description=f"Organization for {user_data.organization_name}",
                        subscription_type=SubscriptionType.TRIAL,
                        is_active=True
                    )
                    db.add(org)
                    db.commit()
                    db.refresh(org)
                    logger.info(f"Organization created with ID: {org.id}")
                else:
                    logger.debug(f"Using existing organization with ID: {org.id}")
                organization_id = org.id
            except Exception as e:
                logger.error(f"Failed to create organization '{user_data.organization_name}': {str(e)}", exc_info=True)
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create organization: {str(e)}"
                )
        
        # Convert UserRegister to UserCreate with proper fields
        logger.debug("Creating user data object...")
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
            role=UserRole.ENGINEER,  # Default role for new users
            timezone="UTC",  # Default timezone
            language="en",  # Default language
            organization_id=organization_id
        )
        
        # Create user
        logger.debug("Creating user in database...")
        try:
            user = user_crud.create(db, obj_in=user_create_data)
            logger.info(f"User created successfully with ID: {user.id}")
        except Exception as e:
            logger.error(f"Failed to create user '{user_data.email}': {str(e)}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
        
        # Create tokens
        logger.debug("Creating access tokens...")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, 
            expires_delta=access_token_expires,
            additional_claims={"role": user.role, "org_id": user.organization_id}
        )
        
        refresh_token = create_refresh_token(subject=user.id)
        
        logger.info(f"Registration completed successfully for: {user_data.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserResponse.from_orm(user)
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error during registration for '{user_data.email}': {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


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
