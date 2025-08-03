"""
Enhanced security middleware for comprehensive application protection.

Implements security headers, input validation, rate limiting, 
and threat detection for production security.
"""

import re
import json
import time
import hashlib
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.cache_service import cache_service

logger = get_logger(__name__)


class SecurityHeaders:
    """Security headers configuration and management."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get comprehensive security headers."""
        return {
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # Prevent content type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            ),
            
            # HSTS (HTTP Strict Transport Security)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Permissions policy
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "interest-cohort=(), accelerometer=(), gyroscope=(), "
                "magnetometer=(), payment=(), usb=()"
            ),
            
            # Server information hiding
            "Server": "Vessel-Guard-API",
            
            # Cache control for sensitive responses
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }


class InputSanitizer:
    """Input sanitization and validation."""
    
    def __init__(self):
        # Common XSS patterns
        self.xss_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'onload\s*=', re.IGNORECASE),
            re.compile(r'onerror\s*=', re.IGNORECASE),
            re.compile(r'onclick\s*=', re.IGNORECASE),
            re.compile(r'onmouseover\s*=', re.IGNORECASE),
            re.compile(r'alert\s*\(', re.IGNORECASE),
            re.compile(r'confirm\s*\(', re.IGNORECASE),
            re.compile(r'prompt\s*\(', re.IGNORECASE),
            re.compile(r'document\.cookie', re.IGNORECASE),
            re.compile(r'window\.location', re.IGNORECASE),
            re.compile(r'eval\s*\(', re.IGNORECASE),
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            re.compile(r'union\s+select', re.IGNORECASE),
            re.compile(r'drop\s+table', re.IGNORECASE),
            re.compile(r'insert\s+into', re.IGNORECASE),
            re.compile(r'delete\s+from', re.IGNORECASE),
            re.compile(r'update\s+set', re.IGNORECASE),
            re.compile(r'exec\s*\(', re.IGNORECASE),
            re.compile(r'execute\s*\(', re.IGNORECASE),
            re.compile(r"'\s*or\s*'1'\s*=\s*'1", re.IGNORECASE),
            re.compile(r"'\s*or\s*1\s*=\s*1", re.IGNORECASE),
            re.compile(r"admin'\s*--", re.IGNORECASE),
            re.compile(r"admin'\s*#", re.IGNORECASE),
        ]
        
        # Directory traversal patterns
        self.traversal_patterns = [
            re.compile(r'\.\./', re.IGNORECASE),
            re.compile(r'\.\.\\', re.IGNORECASE),
            re.compile(r'%2e%2e%2f', re.IGNORECASE),
            re.compile(r'%252e%252e%252f', re.IGNORECASE),
        ]
    
    def check_xss(self, text: str) -> bool:
        """Check for XSS patterns."""
        for pattern in self.xss_patterns:
            if pattern.search(text):
                return True
        return False
    
    def check_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns."""
        for pattern in self.sql_patterns:
            if pattern.search(text):
                return True
        return False
    
    def check_directory_traversal(self, text: str) -> bool:
        """Check for directory traversal patterns."""
        for pattern in self.traversal_patterns:
            if pattern.search(text):
                return True
        return False
    
    def sanitize_input(self, data: str) -> str:
        """Sanitize input by removing dangerous patterns."""
        # Remove dangerous script tags
        for pattern in self.xss_patterns:
            data = pattern.sub('', data)
        
        # Basic HTML encoding for remaining content
        data = (data.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
        
        return data


class ThreatDetector:
    """Advanced threat detection system."""
    
    def __init__(self):
        self.suspicious_ips = set()
        self.blocked_ips = set()
        self.request_counts = defaultdict(lambda: deque())
        self.failed_logins = defaultdict(lambda: deque())
        
        # Load blocked IPs from cache if available
        self._load_blocked_ips()
    
    def _load_blocked_ips(self):
        """Load blocked IPs from cache."""
        try:
            cached_blocked_ips = cache_service.get("security:blocked_ips")
            if cached_blocked_ips:
                self.blocked_ips = set(cached_blocked_ips)
        except Exception as e:
            logger.warning(f"Failed to load blocked IPs: {e}")
    
    def _save_blocked_ips(self):
        """Save blocked IPs to cache."""
        try:
            cache_service.set("security:blocked_ips", list(self.blocked_ips), ttl=3600)
        except Exception as e:
            logger.warning(f"Failed to save blocked IPs: {e}")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        return ip in self.blocked_ips
    
    def block_ip(self, ip: str, duration_minutes: int = 60):
        """Block an IP address."""
        self.blocked_ips.add(ip)
        self._save_blocked_ips()
        
        # Set expiration
        cache_key = f"security:ip_block:{ip}"
        cache_service.set(cache_key, True, ttl=duration_minutes * 60)
        
        logger.warning(f"IP blocked: {ip} for {duration_minutes} minutes")
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address."""
        self.blocked_ips.discard(ip)
        self._save_blocked_ips()
        
        cache_key = f"security:ip_block:{ip}"
        cache_service.delete(cache_key)
        
        logger.info(f"IP unblocked: {ip}")
    
    def check_rate_limit(self, ip: str, max_requests: int = 100, window_minutes: int = 15) -> bool:
        """Check if IP is within rate limits."""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old entries
        requests = self.request_counts[ip]
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Add current request
        requests.append(now)
        
        # Check limit
        if len(requests) > max_requests:
            self.block_ip(ip, duration_minutes=30)
            return False
        
        return True
    
    def record_failed_login(self, ip: str, max_failures: int = 5, window_minutes: int = 15) -> bool:
        """Record failed login and check if IP should be blocked."""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old entries
        failures = self.failed_logins[ip]
        while failures and failures[0] < window_start:
            failures.popleft()
        
        # Add current failure
        failures.append(now)
        
        # Check if IP should be blocked
        if len(failures) >= max_failures:
            self.block_ip(ip, duration_minutes=60)
            return True
        
        return False
    
    def analyze_request_pattern(self, request: Request) -> Dict[str, bool]:
        """Analyze request for suspicious patterns."""
        threats = {
            "bot_detected": False,
            "scanner_detected": False,
            "suspicious_headers": False,
            "malformed_request": False
        }
        
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Bot detection
        bot_patterns = [
            "bot", "crawler", "spider", "scraper", "wget", "curl",
            "python-requests", "go-http-client", "java/", "apache-httpclient"
        ]
        threats["bot_detected"] = any(pattern in user_agent for pattern in bot_patterns)
        
        # Scanner detection
        scanner_patterns = [
            "nmap", "masscan", "zap", "burp", "nikto", "sqlmap",
            "acunetix", "nessus", "openvas", "w3af"
        ]
        threats["scanner_detected"] = any(pattern in user_agent for pattern in scanner_patterns)
        
        # Suspicious headers
        if not request.headers.get("accept"):
            threats["suspicious_headers"] = True
        
        if request.headers.get("x-forwarded-for"):
            # Multiple proxy chains might be suspicious
            proxies = request.headers.get("x-forwarded-for").split(",")
            if len(proxies) > 3:
                threats["suspicious_headers"] = True
        
        # Malformed request detection
        try:
            if request.method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
                threats["malformed_request"] = True
        except Exception:
            threats["malformed_request"] = True
        
        return threats


class EnhancedSecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        self.input_sanitizer = InputSanitizer()
        self.threat_detector = ThreatDetector()
        self.security_headers = SecurityHeaders()
        
        # Paths that bypass security checks
        self.bypass_paths = ["/docs", "/redoc", "/openapi.json"]
        
        # High security paths
        self.high_security_paths = [
            "/api/v1/auth", "/api/v1/users", "/api/v1/admin"
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through security layers."""
        client_ip = self._get_client_ip(request)
        
        # Skip security checks for bypass paths
        if any(request.url.path.startswith(path) for path in self.bypass_paths):
            response = await call_next(request)
            return self._add_security_headers(response)
        
        # Check if IP is blocked
        if self.threat_detector.is_ip_blocked(client_ip):
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied"}
            )
        
        # Rate limiting
        if not self.threat_detector.check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Threat analysis
        threats = self.threat_detector.analyze_request_pattern(request)
        if any(threats.values()):
            logger.warning(f"Threats detected from {client_ip}: {threats}")
            # For now, just log. In production, might block certain patterns
        
        # Input validation for high-security paths
        if any(request.url.path.startswith(path) for path in self.high_security_paths):
            if not await self._validate_input_security(request):
                logger.warning(f"Malicious input detected from {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid input detected"}
                )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Add security headers
            response = self._add_security_headers(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get the real client IP address."""
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
    
    async def _validate_input_security(self, request: Request) -> bool:
        """Validate request input for security threats."""
        try:
            # Check query parameters
            for key, value in request.query_params.items():
                if (self.input_sanitizer.check_xss(value) or
                    self.input_sanitizer.check_sql_injection(value) or
                    self.input_sanitizer.check_directory_traversal(value)):
                    return False
            
            # Check request body if it's JSON
            if request.headers.get("content-type", "").startswith("application/json"):
                try:
                    body = await request.body()
                    if body:
                        body_str = body.decode()
                        if (self.input_sanitizer.check_xss(body_str) or
                            self.input_sanitizer.check_sql_injection(body_str)):
                            return False
                except Exception:
                    # If body parsing fails, it might be malicious
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return False
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        try:
            headers = self.security_headers.get_security_headers()
            
            for header, value in headers.items():
                response.headers[header] = value
            
            # Add custom headers
            response.headers["X-Request-ID"] = getattr(response, "request_id", "unknown")
            response.headers["X-Security-Score"] = "100"  # Could be dynamic based on threats
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to add security headers: {e}")
            return response


class SecurityConfig:
    """Security configuration management."""
    
    @staticmethod
    def get_password_policy() -> Dict[str, Any]:
        """Get password policy configuration."""
        return {
            "min_length": 12,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": True,
            "min_special_chars": 1,
            "max_repeated_chars": 2,
            "password_history": 5,  # Remember last 5 passwords
            "expiry_days": 90,
            "lockout_attempts": 5,
            "lockout_duration_minutes": 30
        }
    
    @staticmethod
    def get_session_policy() -> Dict[str, Any]:
        """Get session security policy."""
        return {
            "max_age_minutes": 480,  # 8 hours
            "idle_timeout_minutes": 60,
            "require_https": True,
            "secure_cookies": True,
            "same_site": "strict",
            "regenerate_on_login": True,
            "max_concurrent_sessions": 3
        }
    
    @staticmethod
    def get_api_security_config() -> Dict[str, Any]:
        """Get API security configuration."""
        return {
            "rate_limit_per_minute": 60,
            "rate_limit_per_hour": 1000,
            "max_request_size_mb": 10,
            "allowed_file_types": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"],
            "max_file_size_mb": 25,
            "require_authentication": True,
            "cors_max_age": 3600,
            "api_key_required": False  # For future API key implementation
        }


# Helper functions for password validation
def validate_password_strength(password: str) -> Dict[str, bool]:
    """Validate password against security policy."""
    policy = SecurityConfig.get_password_policy()
    
    validation = {
        "length_valid": len(password) >= policy["min_length"],
        "has_uppercase": bool(re.search(r'[A-Z]', password)) if policy["require_uppercase"] else True,
        "has_lowercase": bool(re.search(r'[a-z]', password)) if policy["require_lowercase"] else True,
        "has_numbers": bool(re.search(r'\d', password)) if policy["require_numbers"] else True,
        "has_special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)) if policy["require_special_chars"] else True,
        "no_repeated": not bool(re.search(r'(.)\1{' + str(policy["max_repeated_chars"]) + ',}', password)),
        "not_common": not _is_common_password(password)
    }
    
    validation["is_valid"] = all(validation.values())
    return validation


def _is_common_password(password: str) -> bool:
    """Check if password is in common passwords list."""
    # In production, this would check against a comprehensive list
    common_passwords = [
        "password", "123456", "123456789", "12345678", "12345",
        "1234567", "admin", "administrator", "root", "user",
        "guest", "test", "demo", "qwerty", "abc123", "password123"
    ]
    return password.lower() in common_passwords


def generate_security_token() -> str:
    """Generate a secure random token."""
    import secrets
    return secrets.token_urlsafe(32)


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for secure storage."""
    return hashlib.sha256(data.encode()).hexdigest()


# Create global instances
input_sanitizer = InputSanitizer()
threat_detector = ThreatDetector()
security_config = SecurityConfig()