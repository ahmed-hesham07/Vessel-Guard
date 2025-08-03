"""
Response optimization middleware for enhanced API performance.

Provides response compression, caching headers, field selection,
and response time optimization for improved user experience.
"""

import gzip
import json
import time
from typing import Optional, Set, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.datastructures import MutableHeaders

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ResponseCompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for response compression to reduce bandwidth usage."""
    
    def __init__(
        self,
        app,
        minimum_size: int = 1024,
        compression_level: int = 6,
        excluded_paths: Optional[Set[str]] = None
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.excluded_paths = excluded_paths or {
            "/docs", "/redoc", "/openapi.json", "/favicon.ico"
        }
        
        # MIME types that should be compressed
        self.compressible_types = {
            "application/json",
            "application/javascript",
            "text/html",
            "text/css",
            "text/plain",
            "text/xml",
            "application/xml",
            "application/xhtml+xml"
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply response compression if appropriate."""
        # Skip compression for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Check if client accepts gzip compression
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return await call_next(request)
        
        # Process the request
        response = await call_next(request)
        
        # Only compress if it's worth it
        if not self._should_compress(response):
            return response
        
        # Apply compression
        return await self._compress_response(response)
    
    def _should_compress(self, response: Response) -> bool:
        """Determine if response should be compressed."""
        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0].strip()
        if content_type not in self.compressible_types:
            return False
        
        # Check if already compressed
        if response.headers.get("content-encoding"):
            return False
        
        # Check content length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.minimum_size:
            return False
        
        return True
    
    async def _compress_response(self, response: Response) -> Response:
        """Compress the response content."""
        try:
            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Skip compression if body is too small
            if len(body) < self.minimum_size:
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=response.headers,
                    media_type=response.media_type
                )
            
            # Compress the body
            compressed_body = gzip.compress(body, compresslevel=self.compression_level)
            
            # Update headers
            headers = MutableHeaders(response.headers)
            headers["content-encoding"] = "gzip"
            headers["content-length"] = str(len(compressed_body))
            headers["vary"] = "Accept-Encoding"
            
            logger.debug(f"Compressed response: {len(body)} -> {len(compressed_body)} bytes")
            
            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type
            )
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return response


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding appropriate cache headers to responses."""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Cache policies for different endpoint types
        self.cache_policies = {
            # Static resources
            "/docs": {"max_age": 3600, "public": True},
            "/redoc": {"max_age": 3600, "public": True},
            "/openapi.json": {"max_age": 300, "public": True},
            
            # Health checks - short cache
            "/api/v1/health": {"max_age": 60, "public": True},
            "/api/v1/status": {"max_age": 300, "public": True},
            
            # Reference data - longer cache
            "/api/v1/materials": {"max_age": 1800, "public": False},
            "/api/v1/organizations": {"max_age": 900, "public": False},
            
            # User data - no cache
            "/api/v1/users": {"no_cache": True},
            "/api/v1/auth": {"no_cache": True},
            "/api/v1/audit": {"no_cache": True},
            
            # Dynamic data - short cache
            "/api/v1/projects": {"max_age": 300, "public": False, "must_revalidate": True},
            "/api/v1/calculations": {"max_age": 300, "public": False, "must_revalidate": True},
            "/api/v1/reports": {"max_age": 600, "public": False},
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Add appropriate cache headers based on endpoint."""
        response = await call_next(request)
        
        # Find matching cache policy
        cache_policy = self._get_cache_policy(request.url.path)
        
        if cache_policy:
            self._apply_cache_headers(response, cache_policy)
        
        return response
    
    def _get_cache_policy(self, path: str) -> Optional[Dict[str, Any]]:
        """Get cache policy for the given path."""
        # Check for exact matches first
        if path in self.cache_policies:
            return self.cache_policies[path]
        
        # Check for prefix matches
        for pattern, policy in self.cache_policies.items():
            if path.startswith(pattern):
                return policy
        
        # Default policy for API endpoints
        if path.startswith("/api/"):
            return {"max_age": 0, "no_cache": True}
        
        return None
    
    def _apply_cache_headers(self, response: Response, policy: Dict[str, Any]):
        """Apply cache headers based on policy."""
        headers = MutableHeaders(response.headers)
        
        if policy.get("no_cache"):
            headers["cache-control"] = "no-cache, no-store, must-revalidate"
            headers["pragma"] = "no-cache"
            headers["expires"] = "0"
        else:
            cache_control_parts = []
            
            if policy.get("public"):
                cache_control_parts.append("public")
            else:
                cache_control_parts.append("private")
            
            if "max_age" in policy:
                cache_control_parts.append(f"max-age={policy['max_age']}")
            
            if policy.get("must_revalidate"):
                cache_control_parts.append("must-revalidate")
            
            headers["cache-control"] = ", ".join(cache_control_parts)
        
        # Add ETag for better caching
        if response.status_code == 200 and not policy.get("no_cache"):
            # Simple ETag based on content length and last modified
            etag_content = f"{len(response.body) if hasattr(response, 'body') else 0}"
            headers["etag"] = f'"{hash(etag_content) % 10**8}"'


class FieldSelectionMiddleware(BaseHTTPMiddleware):
    """Middleware for response field selection to reduce response size."""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply field selection if requested."""
        response = await call_next(request)
        
        # Only process JSON responses
        if not self._is_json_response(response):
            return response
        
        # Check for field selection parameters
        fields = request.query_params.get("fields")
        exclude = request.query_params.get("exclude")
        
        if not fields and not exclude:
            return response
        
        # Apply field selection
        return await self._apply_field_selection(response, fields, exclude)
    
    def _is_json_response(self, response: Response) -> bool:
        """Check if response is JSON."""
        content_type = response.headers.get("content-type", "")
        return "application/json" in content_type
    
    async def _apply_field_selection(
        self, 
        response: Response, 
        fields: Optional[str], 
        exclude: Optional[str]
    ) -> Response:
        """Apply field selection to JSON response."""
        try:
            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Parse JSON
            data = json.loads(body.decode())
            
            # Apply field selection
            if isinstance(data, dict):
                data = self._filter_dict(data, fields, exclude)
            elif isinstance(data, list):
                data = [self._filter_dict(item, fields, exclude) for item in data]
            
            # Create new response
            new_body = json.dumps(data, separators=(',', ':')).encode()
            
            headers = MutableHeaders(response.headers)
            headers["content-length"] = str(len(new_body))
            
            return Response(
                content=new_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type
            )
            
        except Exception as e:
            logger.warning(f"Field selection failed: {e}")
            return response
    
    def _filter_dict(
        self, 
        data: Dict[str, Any], 
        fields: Optional[str], 
        exclude: Optional[str]
    ) -> Dict[str, Any]:
        """Filter dictionary based on field selection."""
        if not isinstance(data, dict):
            return data
        
        # Parse field lists
        include_fields = set(fields.split(",")) if fields else None
        exclude_fields = set(exclude.split(",")) if exclude else set()
        
        filtered = {}
        
        for key, value in data.items():
            # Skip excluded fields
            if key in exclude_fields:
                continue
            
            # Include only specified fields if include_fields is set
            if include_fields and key not in include_fields:
                continue
            
            # Recursively filter nested objects
            if isinstance(value, dict):
                value = self._filter_dict(value, fields, exclude)
            elif isinstance(value, list):
                value = [
                    self._filter_dict(item, fields, exclude) if isinstance(item, dict) else item
                    for item in value
                ]
            
            filtered[key] = value
        
        return filtered


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking and optimizing response times."""
    
    def __init__(self, app, slow_request_threshold: float = 2.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Track response time and add headers."""
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Add response time header
        headers = MutableHeaders(response.headers)
        headers["x-response-time"] = f"{process_time:.3f}s"
        
        # Log slow requests
        if process_time > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} - {process_time:.3f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "response_time": process_time,
                    "status_code": response.status_code,
                    "query_params": dict(request.query_params) if request.query_params else None
                }
            )
        
        # Add performance hints
        if process_time > 1.0:
            headers["x-performance-hint"] = "Consider pagination or field selection"
        
        return response


class ResponseSizeMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking response sizes and providing optimization hints."""
    
    def __init__(self, app, large_response_threshold: int = 1024 * 1024):  # 1MB
        super().__init__(app)
        self.large_response_threshold = large_response_threshold
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Track response size and add optimization hints."""
        response = await call_next(request)
        
        # Get response size
        content_length = response.headers.get("content-length")
        if content_length:
            size = int(content_length)
            
            headers = MutableHeaders(response.headers)
            
            # Add optimization hints for large responses
            if size > self.large_response_threshold:
                optimization_hints = []
                
                # Check if pagination is being used
                if "page" not in request.query_params:
                    optimization_hints.append("use pagination")
                
                # Check if field selection could help
                if "fields" not in request.query_params:
                    optimization_hints.append("use field selection")
                
                # Check if compression is applied
                if not response.headers.get("content-encoding"):
                    optimization_hints.append("enable compression")
                
                if optimization_hints:
                    headers["x-optimization-hint"] = "; ".join(optimization_hints)
                
                logger.info(
                    f"Large response: {request.method} {request.url.path} - {size} bytes",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "response_size": size,
                        "status_code": response.status_code
                    }
                )
        
        return response