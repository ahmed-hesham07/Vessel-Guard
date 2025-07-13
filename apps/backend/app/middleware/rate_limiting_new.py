"""
Enhanced rate limiting middleware with Redis backend, multiple rate limits,
and comprehensive monitoring.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import redis.asyncio as redis
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging_config import get_logger, log_security_event


class RateLimitType(Enum):
    """Rate limit types."""
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_ENDPOINT = "per_endpoint"
    GLOBAL = "global"


@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests: int
    window_seconds: int
    limit_type: RateLimitType
    identifier: Optional[str] = None
    burst_allowance: int = 0  # Allow burst requests
    
    def __post_init__(self):
        if self.burst_allowance < 0:
            self.burst_allowance = 0


@dataclass
class RateLimitResult:
    """Rate limit check result."""
    allowed: bool
    remaining: int
    reset_at: int
    retry_after: Optional[int] = None
    limit_type: Optional[RateLimitType] = None
    identifier: Optional[str] = None


class MemoryRateLimiter:
    """In-memory rate limiter for development/testing."""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.logger = get_logger('vessel_guard.rate_limiter.memory')
    
    async def check_rate_limit(self, key: str, rate_limit: RateLimit) -> RateLimitResult:
        """Check rate limit using in-memory storage."""
        current_time = time.time()
        window_start = current_time - rate_limit.window_seconds
        
        # Clean old requests
        if key in self.requests:
            self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        else:
            self.requests[key] = []
        
        request_count = len(self.requests[key])
        allowed_requests = rate_limit.requests + rate_limit.burst_allowance
        
        if request_count >= allowed_requests:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=int(window_start + rate_limit.window_seconds),
                retry_after=rate_limit.window_seconds,
                limit_type=rate_limit.limit_type,
                identifier=key
            )
        
        # Add current request
        self.requests[key].append(current_time)
        
        return RateLimitResult(
            allowed=True,
            remaining=allowed_requests - request_count - 1,
            reset_at=int(window_start + rate_limit.window_seconds),
            limit_type=rate_limit.limit_type,
            identifier=key
        )


class RedisRateLimiter:
    """Redis-based rate limiter for production."""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.logger = get_logger('vessel_guard.rate_limiter.redis')
    
    async def check_rate_limit(self, key: str, rate_limit: RateLimit) -> RateLimitResult:
        """Check rate limit using Redis sliding window."""
        current_time = time.time()
        window_start = current_time - rate_limit.window_seconds
        
        pipe = self.redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        pipe.zcard(key)
        
        # Add current request with score as timestamp
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipe.expire(key, rate_limit.window_seconds + 1)
        
        try:
            results = await pipe.execute()
            request_count = results[1]  # Count after cleanup
            
            allowed_requests = rate_limit.requests + rate_limit.burst_allowance
            
            if request_count >= allowed_requests:
                # Remove the request we just added since it's not allowed
                await self.redis_client.zrem(key, str(current_time))
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=int(current_time + rate_limit.window_seconds),
                    retry_after=rate_limit.window_seconds,
                    limit_type=rate_limit.limit_type,
                    identifier=key
                )
            
            return RateLimitResult(
                allowed=True,
                remaining=allowed_requests - request_count - 1,
                reset_at=int(current_time + rate_limit.window_seconds),
                limit_type=rate_limit.limit_type,
                identifier=key
            )
            
        except Exception as e:
            self.logger.error(f"Redis rate limit error: {e}")
            # Fall back to allowing the request on Redis errors
            return RateLimitResult(
                allowed=True,
                remaining=0,
                reset_at=int(current_time + rate_limit.window_seconds),
                limit_type=rate_limit.limit_type,
                identifier=key
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enhanced rate limiting middleware with multiple limits and monitoring."""
    
    def __init__(self, app, redis_url: Optional[str] = None):
        super().__init__(app)
        
        if redis_url:
            self.limiter = RedisRateLimiter(redis_url)
        else:
            self.limiter = MemoryRateLimiter()
        
        self.logger = get_logger('vessel_guard.rate_limiting')
        
        # Rate limit configurations
        self.rate_limits = self._configure_rate_limits()
        
        # Whitelist for certain IPs (like health checks)
        self.whitelisted_ips = set(getattr(settings, 'RATE_LIMIT_WHITELIST', []))
        
        # Paths that should be excluded from rate limiting
        self.excluded_paths = {
            '/health',
            '/health/liveness',
            '/health/readiness',
            '/health/detailed',
            '/health/system',
            '/docs',
            '/redoc',
            '/openapi.json'
        }
    
    def _configure_rate_limits(self) -> List[RateLimit]:
        """Configure rate limits based on environment."""
        if hasattr(settings, 'ENVIRONMENT') and settings.ENVIRONMENT == 'production':
            return [
                # Strict production limits
                RateLimit(requests=1000, window_seconds=3600, limit_type=RateLimitType.PER_IP),  # Per hour per IP
                RateLimit(requests=100, window_seconds=60, limit_type=RateLimitType.PER_IP),     # Per minute per IP
                RateLimit(requests=10000, window_seconds=3600, limit_type=RateLimitType.PER_USER), # Per hour per user
                RateLimit(requests=50000, window_seconds=3600, limit_type=RateLimitType.GLOBAL),   # Global limit
            ]
        else:
            return [
                # Development limits
                RateLimit(requests=10000, window_seconds=3600, limit_type=RateLimitType.PER_IP),
                RateLimit(requests=1000, window_seconds=60, limit_type=RateLimitType.PER_IP),
                RateLimit(requests=50000, window_seconds=3600, limit_type=RateLimitType.PER_USER),
                RateLimit(requests=100000, window_seconds=3600, limit_type=RateLimitType.GLOBAL),
            ]
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier (IP address with forwarded headers support)."""
        # Check for forwarded headers (load balancer, proxy)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else 'unknown'
    
    def _get_user_identifier(self, request: Request) -> Optional[str]:
        """Get user identifier if authenticated."""
        # This would be set by authentication middleware
        return getattr(request.state, 'user_id', None)
    
    def _should_skip_rate_limiting(self, request: Request, client_ip: str) -> bool:
        """Check if request should skip rate limiting."""
        # Skip for whitelisted IPs
        if client_ip in self.whitelisted_ips:
            return True
        
        # Skip for excluded paths
        if request.url.path in self.excluded_paths:
            return True
        
        # Skip for health check user agents
        user_agent = request.headers.get('User-Agent', '').lower()
        if any(agent in user_agent for agent in ['kube-probe', 'docker', 'health-check']):
            return True
        
        return False
    
    async def _check_all_limits(self, request: Request, client_ip: str, user_id: Optional[str]) -> Optional[RateLimitResult]:
        """Check all applicable rate limits."""
        results = []
        
        for rate_limit in self.rate_limits:
            key = None
            
            if rate_limit.limit_type == RateLimitType.PER_IP:
                key = f"ip:{client_ip}"
            elif rate_limit.limit_type == RateLimitType.PER_USER and user_id:
                key = f"user:{user_id}"
            elif rate_limit.limit_type == RateLimitType.PER_ENDPOINT:
                key = f"endpoint:{request.method}:{request.url.path}"
            elif rate_limit.limit_type == RateLimitType.GLOBAL:
                key = "global"
            
            if key:
                result = await self.limiter.check_rate_limit(key, rate_limit)
                if not result.allowed:
                    return result
                results.append(result)
        
        # Return the most restrictive result
        if results:
            return min(results, key=lambda r: r.remaining)
        
        return None
    
    def _create_rate_limit_response(self, result: RateLimitResult) -> Response:
        """Create rate limit exceeded response."""
        headers = {
            'X-RateLimit-Limit': str(result.remaining + 1),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': str(result.reset_at),
        }
        
        if result.retry_after:
            headers['Retry-After'] = str(result.retry_after)
        
        content = {
            'error': 'rate_limit_exceeded',
            'message': 'Too many requests. Please try again later.',
            'limit_type': result.limit_type.value if result.limit_type else 'unknown',
            'retry_after': result.retry_after
        }
        
        return JSONResponse(
            status_code=429,
            content=content,
            headers=headers
        )
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        start_time = time.time()
        
        # Get client identifier
        client_ip = self._get_client_identifier(request)
        user_id = self._get_user_identifier(request)
        
        # Check if we should skip rate limiting
        if self._should_skip_rate_limiting(request, client_ip):
            return await call_next(request)
        
        try:
            # Check rate limits
            result = await self._check_all_limits(request, client_ip, user_id)
            
            if result and not result.allowed:
                # Log rate limit violation
                log_security_event(
                    'rate_limit_exceeded',
                    {
                        'client_ip': client_ip,
                        'user_id': user_id,
                        'path': request.url.path,
                        'method': request.method,
                        'limit_type': result.limit_type.value if result.limit_type else 'unknown',
                        'identifier': result.identifier
                    },
                    severity='WARNING'
                )
                
                return self._create_rate_limit_response(result)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to successful responses
            if result:
                response.headers['X-RateLimit-Limit'] = str(result.remaining + 1)
                response.headers['X-RateLimit-Remaining'] = str(result.remaining)
                response.headers['X-RateLimit-Reset'] = str(result.reset_at)
            
            # Log successful request with rate limit info
            duration_ms = (time.time() - start_time) * 1000
            self.logger.debug(
                f"Request processed: {request.method} {request.url.path}",
                extra={
                    'client_ip': client_ip,
                    'user_id': user_id,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'rate_limit_remaining': result.remaining if result else None
                }
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Rate limiting error: {e}", exc_info=True)
            # Continue with request on middleware errors
            return await call_next(request)
