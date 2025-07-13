"""
Security middleware for comprehensive application protection.

Implements security headers, request filtering, IP blocking, and threat detection.
"""

import time
import re
import hashlib
import hmac
from typing import Set, Dict, List, Optional, Pattern
from dataclasses import dataclass
from ipaddress import ip_address, ip_network, AddressValueError

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import get_logger, log_security_event


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    # Security headers
    enable_security_headers: bool = True
    enable_hsts: bool = True
    hsts_max_age: int = 31536000  # 1 year
    enable_csp: bool = True
    csp_policy: str = "default-src 'self'"
    
    # Request filtering
    enable_request_filtering: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    blocked_user_agents: List[str] = None
    blocked_ips: Set[str] = None
    allowed_origins: List[str] = None
    
    # Threat detection
    enable_threat_detection: bool = True
    suspicious_patterns: List[str] = None
    max_failed_attempts: int = 5
    lockout_duration: int = 300  # 5 minutes
    
    def __post_init__(self):
        if self.blocked_user_agents is None:
            self.blocked_user_agents = [
                r'(?i)bot',
                r'(?i)crawler',
                r'(?i)spider',
                r'(?i)scraper',
                r'(?i)curl',
                r'(?i)wget',
                r'(?i)python-requests',
                r'(?i)masscan',
                r'(?i)nmap',
                r'(?i)nikto'
            ]
        
        if self.blocked_ips is None:
            self.blocked_ips = set()
        
        if self.allowed_origins is None:
            self.allowed_origins = ['*']  # Default to allow all in development
        
        if self.suspicious_patterns is None:
            self.suspicious_patterns = [
                # SQL injection patterns
                r'(?i)(union\s+select|select\s+.*\s+from|insert\s+into|delete\s+from|drop\s+table)',
                # XSS patterns
                r'(?i)(<script|javascript:|on\w+\s*=)',
                # Path traversal
                r'(\.\.\/|\.\.\\)',
                # Command injection
                r'(?i)(;|\||&|\$\(|\`)',
                # LDAP injection
                r'(\*\)|\|\||\&\&)',
                # XML injection
                r'(?i)(<!entity|<!doctype)',
            ]


class ThreatDetector:
    """Threat detection and tracking."""
    
    def __init__(self):
        self.failed_attempts: Dict[str, List[float]] = {}
        self.blocked_ips: Set[str] = set()
        self.logger = get_logger('vessel_guard.security.threat_detector')
    
    def record_failed_attempt(self, client_ip: str, config: SecurityConfig):
        """Record a failed attempt and check if IP should be blocked."""
        current_time = time.time()
        
        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = []
        
        # Clean old attempts
        cutoff_time = current_time - config.lockout_duration
        self.failed_attempts[client_ip] = [
            attempt_time for attempt_time in self.failed_attempts[client_ip]
            if attempt_time > cutoff_time
        ]
        
        # Add current attempt
        self.failed_attempts[client_ip].append(current_time)
        
        # Check if IP should be blocked
        if len(self.failed_attempts[client_ip]) >= config.max_failed_attempts:
            self.blocked_ips.add(client_ip)
            
            log_security_event(
                'ip_blocked_threat_detection',
                {
                    'client_ip': client_ip,
                    'failed_attempts': len(self.failed_attempts[client_ip]),
                    'lockout_duration': config.lockout_duration
                },
                severity='WARNING'
            )
            
            return True
        
        return False
    
    def is_ip_blocked(self, client_ip: str, config: SecurityConfig) -> bool:
        """Check if IP is currently blocked."""
        if client_ip not in self.blocked_ips:
            return False
        
        # Check if block has expired
        current_time = time.time()
        if client_ip in self.failed_attempts:
            last_attempt = max(self.failed_attempts[client_ip])
            if current_time - last_attempt > config.lockout_duration:
                self.blocked_ips.discard(client_ip)
                del self.failed_attempts[client_ip]
                return False
        
        return True
    
    def check_suspicious_patterns(self, request: Request, config: SecurityConfig) -> List[str]:
        """Check request for suspicious patterns."""
        suspicious_findings = []
        
        # Check URL path
        for pattern in config.suspicious_patterns:
            if re.search(pattern, str(request.url)):
                suspicious_findings.append(f"URL pattern: {pattern}")
        
        # Check query parameters
        for key, value in request.query_params.items():
            for pattern in config.suspicious_patterns:
                if re.search(pattern, f"{key}={value}"):
                    suspicious_findings.append(f"Query param pattern: {pattern}")
        
        # Check headers
        for header_name, header_value in request.headers.items():
            for pattern in config.suspicious_patterns:
                if re.search(pattern, f"{header_name}: {header_value}"):
                    suspicious_findings.append(f"Header pattern: {pattern}")
        
        return suspicious_findings


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware."""
    
    def __init__(self, app, config: Optional[SecurityConfig] = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.threat_detector = ThreatDetector()
        self.logger = get_logger('vessel_guard.security.middleware')
        
        # Compile regex patterns for performance
        self.blocked_user_agent_patterns = [
            re.compile(pattern) for pattern in self.config.blocked_user_agents
        ]
        
        # Initialize configuration based on environment
        self._configure_for_environment()
    
    def _configure_for_environment(self):
        """Configure security settings based on environment."""
        environment = getattr(settings, 'ENVIRONMENT', 'development')
        
        if environment == 'production':
            # Strict production settings
            self.config.enable_hsts = True
            self.config.enable_csp = True
            self.config.csp_policy = "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none';"
            self.config.allowed_origins = getattr(settings, 'ALLOWED_ORIGINS', ['https://vesselguard.com'])
        else:
            # Development settings
            self.config.enable_hsts = False
            self.config.csp_policy = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: http: https:;"
            self.config.allowed_origins = ['*']
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support."""
        # Check for forwarded headers
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else 'unknown'
    
    def _is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is in blocked list."""
        # Check static blocked IPs
        if client_ip in self.config.blocked_ips:
            return True
        
        # Check threat detection blocks
        return self.threat_detector.is_ip_blocked(client_ip, self.config)
    
    def _is_user_agent_blocked(self, user_agent: str) -> bool:
        """Check if user agent is blocked."""
        for pattern in self.blocked_user_agent_patterns:
            if pattern.search(user_agent):
                return True
        return False
    
    def _check_origin(self, request: Request) -> bool:
        """Check if origin is allowed."""
        if '*' in self.config.allowed_origins:
            return True
        
        origin = request.headers.get('Origin', '')
        if not origin:
            return True  # Allow requests without origin header
        
        return origin in self.config.allowed_origins
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        if not self.config.enable_security_headers:
            return
        
        # HSTS
        if self.config.enable_hsts:
            response.headers['Strict-Transport-Security'] = f'max-age={self.config.hsts_max_age}; includeSubDomains'
        
        # Content Security Policy
        if self.config.enable_csp:
            response.headers['Content-Security-Policy'] = self.config.csp_policy
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        # Remove server information
        response.headers.pop('Server', None)
    
    def _create_security_response(self, message: str, status_code: int = 403) -> Response:
        """Create security violation response."""
        return JSONResponse(
            status_code=status_code,
            content={
                'error': 'security_violation',
                'message': message
            }
        )
    
    async def dispatch(self, request: Request, call_next):
        """Process request with security checks."""
        start_time = time.time()
        
        # Skip security checks for health endpoints
        if request.url.path.startswith('/health'):
            response = await call_next(request)
            self._add_security_headers(response)
            return response
        
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get('User-Agent', '')
        
        try:
            # Check IP blocking
            if self._is_ip_blocked(client_ip):
                log_security_event(
                    'blocked_ip_access_attempt',
                    {
                        'client_ip': client_ip,
                        'path': request.url.path,
                        'user_agent': user_agent
                    },
                    severity='WARNING'
                )
                return self._create_security_response('Access denied: IP blocked')
            
            # Check user agent blocking
            if self.config.enable_request_filtering and self._is_user_agent_blocked(user_agent):
                log_security_event(
                    'blocked_user_agent',
                    {
                        'client_ip': client_ip,
                        'user_agent': user_agent,
                        'path': request.url.path
                    },
                    severity='INFO'
                )
                return self._create_security_response('Access denied: User agent not allowed')
            
            # Check origin
            if not self._check_origin(request):
                log_security_event(
                    'invalid_origin',
                    {
                        'client_ip': client_ip,
                        'origin': request.headers.get('Origin', ''),
                        'path': request.url.path
                    },
                    severity='WARNING'
                )
                return self._create_security_response('Access denied: Invalid origin')
            
            # Check request size
            content_length = request.headers.get('Content-Length')
            if content_length and int(content_length) > self.config.max_request_size:
                log_security_event(
                    'request_too_large',
                    {
                        'client_ip': client_ip,
                        'content_length': content_length,
                        'max_size': self.config.max_request_size
                    },
                    severity='WARNING'
                )
                return self._create_security_response('Request too large', 413)
            
            # Threat detection
            if self.config.enable_threat_detection:
                suspicious_patterns = self.threat_detector.check_suspicious_patterns(request, self.config)
                if suspicious_patterns:
                    # Record as suspicious activity
                    self.threat_detector.record_failed_attempt(client_ip, self.config)
                    
                    log_security_event(
                        'suspicious_request_pattern',
                        {
                            'client_ip': client_ip,
                            'patterns': suspicious_patterns,
                            'path': request.url.path,
                            'user_agent': user_agent
                        },
                        severity='WARNING'
                    )
                    
                    return self._create_security_response('Request contains suspicious patterns')
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            # Log successful request
            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"Security check passed: {request.method} {request.url.path}",
                extra={
                    'client_ip': client_ip,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'user_agent_truncated': user_agent[:100]
                }
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Security middleware error: {e}", exc_info=True)
            
            # Log the error but continue with request
            log_security_event(
                'security_middleware_error',
                {
                    'client_ip': client_ip,
                    'error': str(e),
                    'path': request.url.path
                },
                severity='ERROR'
            )
            
            response = await call_next(request)
            self._add_security_headers(response)
            return response


# Utility functions for external use

def is_safe_redirect_url(url: str, allowed_domains: List[str]) -> bool:
    """Check if a redirect URL is safe."""
    if not url:
        return False
    
    # Check for protocol-relative URLs
    if url.startswith('//'):
        return False
    
    # Check for absolute URLs
    if url.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return any(parsed.netloc.endswith(domain) for domain in allowed_domains)
    
    # Relative URLs are generally safe
    return not url.startswith('/')


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input."""
    if not text:
        return ''
    
    # Truncate
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def generate_csrf_token(secret_key: str, user_id: str) -> str:
    """Generate CSRF token."""
    timestamp = str(int(time.time()))
    message = f"{user_id}:{timestamp}"
    signature = hashlib.hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return f"{message}:{signature}"


def verify_csrf_token(token: str, secret_key: str, user_id: str, max_age: int = 3600) -> bool:
    """Verify CSRF token."""
    try:
        parts = token.split(':')
        if len(parts) != 3:
            return False
        
        token_user_id, timestamp, signature = parts
        
        # Check user ID
        if token_user_id != user_id:
            return False
        
        # Check age
        token_time = int(timestamp)
        if time.time() - token_time > max_age:
            return False
        
        # Verify signature
        message = f"{token_user_id}:{timestamp}"
        expected_signature = hashlib.hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
        
    except (ValueError, TypeError):
        return False
