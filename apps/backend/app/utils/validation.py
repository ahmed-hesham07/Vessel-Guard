"""
Validation utilities for data validation across the application.
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if not password:
        return False
    
    # Password requirements:
    # - At least 8 characters
    # - At least one uppercase letter
    # - At least one lowercase letter
    # - At least one digit
    # - At least one special character
    
    if len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'\d', password):
        return False
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    if not phone:
        return False
    
    # Simple phone validation - accepts various formats
    pattern = r'^\+?1?[-.\s]?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})$'
    return bool(re.match(pattern, phone))


def validate_subdomain(subdomain: str) -> bool:
    """Validate subdomain format."""
    if not subdomain:
        return False
    
    # Subdomain should be alphanumeric with hyphens, 3-63 characters
    pattern = r'^[a-z0-9]([a-z0-9-]{1,61}[a-z0-9])?$'
    return bool(re.match(pattern, subdomain.lower()))


def validate_tag_number(tag_number: str) -> bool:
    """Validate equipment tag number format."""
    if not tag_number:
        return False
    
    # Tag number should be alphanumeric with hyphens and underscores
    pattern = r'^[A-Z0-9][A-Z0-9_-]*$'
    return bool(re.match(pattern, tag_number.upper()))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    if not filename:
        return "unnamed_file"
    
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Trim underscores from start and end
    sanitized = sanitized.strip('_')
    
    return sanitized or "unnamed_file"


def validate_positive_number(value: float, allow_zero: bool = False) -> bool:
    """Validate that a number is positive."""
    if allow_zero:
        return value >= 0
    return value > 0


def validate_coordinate(latitude: Optional[float], longitude: Optional[float]) -> bool:
    """Validate geographic coordinates."""
    if latitude is None or longitude is None:
        return False
    
    return -90 <= latitude <= 90 and -180 <= longitude <= 180
