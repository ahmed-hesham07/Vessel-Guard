"""
Audit middleware for automatic logging of API requests and security events.

Captures request/response data, user context, and security-relevant
information for compliance and security monitoring.
"""

import time
import json
import uuid
from typing import Callable, Optional, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.services.audit_service import (
    audit_service, 
    AuditEventType, 
    AuditSeverity, 
    AuditContext
)
from app.db.base import get_db
from app.core.security import decode_access_token

logger = get_logger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive audit logging of API requests."""
    
    def __init__(self, app, excluded_paths: Optional[list] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/health", "/status"  # Health check endpoints
        ]
        
        # Sensitive endpoints that require detailed logging
        self.sensitive_endpoints = {
            "/api/v1/auth/login": AuditEventType.LOGIN_SUCCESS,
            "/api/v1/auth/logout": AuditEventType.LOGOUT,
            "/api/v1/auth/password-reset": AuditEventType.PASSWORD_RESET_REQUEST,
            "/api/v1/users": AuditEventType.USER_CREATED,
            "/api/v1/reports": AuditEventType.REPORT_GENERATED,
        }
        
        # Endpoints that handle sensitive data
        self.data_access_endpoints = [
            "/api/v1/projects", "/api/v1/vessels", "/api/v1/calculations",
            "/api/v1/reports", "/api/v1/inspections", "/api/v1/materials"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response for audit logging."""
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract user context
        user_context = await self._extract_user_context(request)
        
        # Create audit context
        audit_context = AuditContext(
            user_id=user_context.get("user_id"),
            organization_id=user_context.get("organization_id"),
            session_id=user_context.get("session_id"),
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            request_id=request_id,
            api_endpoint=request.url.path,
            http_method=request.method
        )
        
        # Check for suspicious patterns
        await self._check_security_patterns(request, audit_context)
        
        # Record request start time
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Log the request/response
            await self._log_request_response(
                request, response, audit_context, process_time
            )
            
            return response
            
        except HTTPException as e:
            # Log HTTP exceptions
            await self._log_http_exception(request, e, audit_context)
            raise
            
        except Exception as e:
            # Log unexpected errors
            await self._log_unexpected_error(request, e, audit_context)
            raise
    
    async def _extract_user_context(self, request: Request) -> Dict[str, Any]:
        """Extract user context from request."""
        context = {}
        
        try:
            # Try to get user from authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = decode_access_token(token)
                    context["user_id"] = payload.get("sub")
                    context["organization_id"] = payload.get("organization_id")
                    context["session_id"] = payload.get("session_id")
                except Exception as e:
                    # Invalid token, but don't fail the request
                    logger.debug(f"Invalid token in audit middleware: {e}")
                    context["authentication_status"] = "invalid_token"
            
            # Try to get session information from cookies
            session_id = request.cookies.get("session_id")
            if session_id:
                context["session_id"] = session_id
                
        except Exception as e:
            logger.warning(f"Failed to extract user context: {e}")
        
        return context
    
    def _get_client_ip(self, request: Request) -> str:
        """Get the real client IP address."""
        # Check for forwarded headers (behind proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    async def _check_security_patterns(
        self, 
        request: Request, 
        audit_context: AuditContext
    ):
        """Check for suspicious security patterns in requests."""
        try:
            # Get database session
            db = next(get_db())
            
            # Check for SQL injection patterns
            await self._check_sql_injection(request, audit_context, db)
            
            # Check for XSS patterns
            await self._check_xss_patterns(request, audit_context, db)
            
            # Check for unusual request patterns
            await self._check_unusual_patterns(request, audit_context, db)
            
            db.close()
            
        except Exception as e:
            logger.error(f"Security pattern check failed: {e}")
    
    async def _check_sql_injection(
        self, 
        request: Request, 
        audit_context: AuditContext, 
        db: Session
    ):
        """Check for SQL injection attempt patterns."""
        sql_patterns = [
            "union select", "drop table", "insert into", "delete from",
            "update set", "exec(", "execute(", "sp_", "xp_",
            "script>", "<script", "javascript:", "vbscript:",
            "onload=", "onerror=", "'; --", "'; #", "' or '1'='1",
            "' or 1=1", "admin'--", "admin' #"
        ]
        
        # Check query parameters
        query_string = str(request.url.query).lower()
        for pattern in sql_patterns:
            if pattern in query_string:
                await self._log_security_event(
                    db, 
                    AuditEventType.SQL_INJECTION_ATTEMPT,
                    f"SQL injection pattern detected: {pattern}",
                    audit_context,
                    {"pattern": pattern, "query_string": query_string}
                )
                break
        
        # Check request body if it's JSON
        try:
            if request.headers.get("content-type", "").startswith("application/json"):
                body = await request.body()
                if body:
                    body_str = body.decode().lower()
                    for pattern in sql_patterns:
                        if pattern in body_str:
                            await self._log_security_event(
                                db,
                                AuditEventType.SQL_INJECTION_ATTEMPT,
                                f"SQL injection pattern in body: {pattern}",
                                audit_context,
                                {"pattern": pattern, "body_detected": True}
                            )
                            break
        except Exception as e:
            # Don't fail the request if body parsing fails
            logger.debug(f"Failed to parse request body for security scan: {e}")
            self._log_audit_event(
                audit_context, 
                AuditEventType.SYSTEM_EVENT,
                "Body parsing failed during security scan",
                audit_context,
                {"error": str(e)}
            )
    
    async def _check_xss_patterns(
        self, 
        request: Request, 
        audit_context: AuditContext, 
        db: Session
    ):
        """Check for XSS attempt patterns."""
        xss_patterns = [
            "<script", "</script>", "javascript:", "vbscript:",
            "onload=", "onerror=", "onclick=", "onmouseover=",
            "alert(", "confirm(", "prompt(", "document.cookie",
            "window.location", "eval(", "expression("
        ]
        
        # Check query parameters
        query_string = str(request.url.query).lower()
        for pattern in xss_patterns:
            if pattern in query_string:
                await self._log_security_event(
                    db,
                    AuditEventType.XSS_ATTEMPT,
                    f"XSS pattern detected: {pattern}",
                    audit_context,
                    {"pattern": pattern, "query_string": query_string}
                )
                break
    
    async def _check_unusual_patterns(
        self, 
        request: Request, 
        audit_context: AuditContext, 
        db: Session
    ):
        """Check for unusual request patterns."""
        # Check for directory traversal
        path_traversal_patterns = ["../", "..\\", "%2e%2e", "%252e%252e"]
        request_path = request.url.path.lower()
        
        for pattern in path_traversal_patterns:
            if pattern in request_path:
                await self._log_security_event(
                    db,
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    f"Directory traversal attempt: {pattern}",
                    audit_context,
                    {"pattern": pattern, "path": request_path}
                )
                break
        
        # Check for unusual user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = [
            "sqlmap", "nikto", "nessus", "burp", "zap", "acunetix",
            "nmap", "masscan", "gobuster", "dirb", "dirbuster"
        ]
        
        for agent in suspicious_agents:
            if agent in user_agent:
                await self._log_security_event(
                    db,
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    f"Suspicious user agent: {agent}",
                    audit_context,
                    {"user_agent": user_agent, "pattern": agent}
                )
                break
    
    async def _log_request_response(
        self,
        request: Request,
        response: Response,
        audit_context: AuditContext,
        process_time: float
    ):
        """Log request/response for audit trail."""
        try:
            db = next(get_db())
            
            # Determine if this is a sensitive endpoint
            is_sensitive = any(
                request.url.path.startswith(endpoint) 
                for endpoint in self.data_access_endpoints
            )
            
            # Skip detailed logging for GET requests on non-sensitive endpoints
            if request.method == "GET" and not is_sensitive and response.status_code == 200:
                db.close()
                return
            
            # Determine event type based on method and endpoint
            event_type = self._determine_event_type(request, response)
            
            # Create description
            description = f"{request.method} {request.url.path} - {response.status_code}"
            
            # Collect request details
            details = {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "query_params": dict(request.query_params) if request.query_params else None,
                "response_size": response.headers.get("content-length"),
            }
            
            # Determine severity based on status code
            if response.status_code >= 500:
                severity = AuditSeverity.HIGH
            elif response.status_code >= 400:
                severity = AuditSeverity.MEDIUM
            else:
                severity = AuditSeverity.LOW
            
            # Log the event
            audit_service.log_event(
                db=db,
                event_type=event_type,
                description=description,
                context=audit_context,
                severity=severity,
                details=details,
                is_sensitive=is_sensitive
            )
            
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to log request/response: {e}")
    
    async def _log_http_exception(
        self,
        request: Request,
        exception: HTTPException,
        audit_context: AuditContext
    ):
        """Log HTTP exceptions for audit trail."""
        try:
            db = next(get_db())
            
            description = f"HTTP {exception.status_code}: {exception.detail}"
            
            details = {
                "method": request.method,
                "path": request.url.path,
                "status_code": exception.status_code,
                "error": exception.detail,
                "query_params": dict(request.query_params) if request.query_params else None
            }
            
            # Determine severity
            if exception.status_code == 401:
                event_type = AuditEventType.ACCESS_DENIED
                severity = AuditSeverity.MEDIUM
            elif exception.status_code == 403:
                event_type = AuditEventType.ACCESS_DENIED
                severity = AuditSeverity.MEDIUM
            elif exception.status_code >= 500:
                event_type = AuditEventType.SUSPICIOUS_ACTIVITY
                severity = AuditSeverity.HIGH
            else:
                event_type = AuditEventType.ACCESS_DENIED
                severity = AuditSeverity.LOW
            
            audit_service.log_event(
                db=db,
                event_type=event_type,
                description=description,
                context=audit_context,
                severity=severity,
                details=details,
                requires_investigation=(exception.status_code in [401, 403])
            )
            
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to log HTTP exception: {e}")
    
    async def _log_unexpected_error(
        self,
        request: Request,
        exception: Exception,
        audit_context: AuditContext
    ):
        """Log unexpected errors for audit trail."""
        try:
            db = next(get_db())
            
            description = f"Unexpected error: {type(exception).__name__}"
            
            details = {
                "method": request.method,
                "path": request.url.path,
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "query_params": dict(request.query_params) if request.query_params else None
            }
            
            audit_service.log_event(
                db=db,
                event_type=AuditEventType.SUSPICIOUS_ACTIVITY,
                description=description,
                context=audit_context,
                severity=AuditSeverity.HIGH,
                details=details,
                requires_investigation=True
            )
            
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to log unexpected error: {e}")
    
    async def _log_security_event(
        self,
        db: Session,
        event_type: AuditEventType,
        description: str,
        audit_context: AuditContext,
        threat_details: Dict[str, Any]
    ):
        """Log security events with high priority."""
        audit_service.log_security_event(
            db=db,
            event_type=event_type,
            description=description,
            context=audit_context,
            threat_details=threat_details,
            severity=AuditSeverity.HIGH
        )
    
    def _determine_event_type(
        self, 
        request: Request, 
        response: Response
    ) -> AuditEventType:
        """Determine the appropriate audit event type."""
        # Check specific endpoints
        if request.url.path in self.sensitive_endpoints:
            return self.sensitive_endpoints[request.url.path]
        
        # Default event types based on HTTP method
        if request.method == "POST":
            if "users" in request.url.path:
                return AuditEventType.USER_CREATED
            elif "projects" in request.url.path:
                return AuditEventType.PROJECT_CREATED
            elif "calculations" in request.url.path:
                return AuditEventType.CALCULATION_CREATED
            else:
                return AuditEventType.ACCESS_GRANTED
        
        elif request.method == "PUT" or request.method == "PATCH":
            if "users" in request.url.path:
                return AuditEventType.USER_UPDATED
            elif "projects" in request.url.path:
                return AuditEventType.PROJECT_UPDATED
            elif "calculations" in request.url.path:
                return AuditEventType.CALCULATION_UPDATED
            else:
                return AuditEventType.ACCESS_GRANTED
        
        elif request.method == "DELETE":
            if "users" in request.url.path:
                return AuditEventType.USER_DELETED
            elif "projects" in request.url.path:
                return AuditEventType.PROJECT_DELETED
            elif "calculations" in request.url.path:
                return AuditEventType.CALCULATION_DELETED
            else:
                return AuditEventType.ACCESS_GRANTED
        
        else:
            return AuditEventType.ACCESS_GRANTED