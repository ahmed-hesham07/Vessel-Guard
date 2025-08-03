"""
Caching service for improving application performance.

Provides query result caching, session caching, and frequently
accessed data caching using Redis.
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CacheService:
    """
    Comprehensive caching service for application performance optimization.
    """
    
    def __init__(self):
        """Initialize cache service with Redis connection."""
        self.redis_client = None
        self.enabled = True
        
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Cache service initialized successfully")
            
        except Exception as e:
            logger.warning(f"Redis unavailable, caching disabled: {e}")
            self.enabled = False
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key from arguments."""
        # Create a hash of all arguments for consistent keys
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"vessel_guard:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
        
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return pickle.loads(cached_data)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (seconds)."""
        if not self.enabled:
            return False
        
        try:
            serialized_value = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def flush_all(self) -> bool:
        """Flush all cache entries."""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False
    
    # High-level caching methods
    
    def cache_query_result(self, prefix: str, result: Any, ttl: int = 300, *args, **kwargs) -> bool:
        """Cache a database query result."""
        cache_key = self._generate_cache_key(f"query:{prefix}", *args, **kwargs)
        return self.set(cache_key, result, ttl)
    
    def get_cached_query_result(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """Get cached database query result."""
        cache_key = self._generate_cache_key(f"query:{prefix}", *args, **kwargs)
        return self.get(cache_key)
    
    def invalidate_query_cache(self, prefix: str) -> int:
        """Invalidate all cached queries for a prefix."""
        pattern = f"vessel_guard:query:{prefix}:*"
        return self.delete_pattern(pattern)
    
    def cache_user_data(self, user_id: int, data: Dict[str, Any], ttl: int = 600) -> bool:
        """Cache user-specific data."""
        cache_key = f"vessel_guard:user:{user_id}:data"
        return self.set(cache_key, data, ttl)
    
    def get_cached_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get cached user data."""
        cache_key = f"vessel_guard:user:{user_id}:data"
        return self.get(cache_key)
    
    def invalidate_user_cache(self, user_id: int) -> int:
        """Invalidate all user-specific cache."""
        pattern = f"vessel_guard:user:{user_id}:*"
        return self.delete_pattern(pattern)
    
    def cache_organization_data(self, org_id: int, data: Dict[str, Any], ttl: int = 900) -> bool:
        """Cache organization-specific data."""
        cache_key = f"vessel_guard:org:{org_id}:data"
        return self.set(cache_key, data, ttl)
    
    def get_cached_organization_data(self, org_id: int) -> Optional[Dict[str, Any]]:
        """Get cached organization data."""
        cache_key = f"vessel_guard:org:{org_id}:data"
        return self.get(cache_key)
    
    def invalidate_organization_cache(self, org_id: int) -> int:
        """Invalidate all organization-specific cache."""
        pattern = f"vessel_guard:org:{org_id}:*"
        return self.delete_pattern(pattern)


# Global cache service instance
cache_service = CacheService()


def cached_query(prefix: str, ttl: int = 300, skip_cache: bool = False):
    """
    Decorator for caching database query results.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        skip_cache: Skip cache if True (useful for testing)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if skip_cache:
                return func(*args, **kwargs)
            
            # Try to get from cache first
            cached_result = cache_service.get_cached_query_result(prefix, *args, **kwargs)
            if cached_result is not None:
                logger.debug(f"Cache hit for {prefix}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache_service.cache_query_result(prefix, result, ttl, *args, **kwargs)
                logger.debug(f"Cached result for {prefix}")
            
            return result
        return wrapper
    return decorator


def cache_dashboard_data(user_id: int, org_id: int, data: Dict[str, Any]) -> bool:
    """Cache dashboard data for quick access."""
    return cache_service.cache_user_data(
        user_id, 
        {"dashboard": data, "timestamp": datetime.utcnow().isoformat()}, 
        ttl=300  # 5 minutes
    )


def get_cached_dashboard_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Get cached dashboard data."""
    cached = cache_service.get_cached_user_data(user_id)
    if cached and "dashboard" in cached:
        # Check if data is still fresh (within 5 minutes)
        timestamp = datetime.fromisoformat(cached["timestamp"])
        if datetime.utcnow() - timestamp < timedelta(minutes=5):
            return cached["dashboard"]
    return None


def invalidate_user_related_cache(user_id: int, org_id: int):
    """Invalidate all cache related to a user and organization."""
    cache_service.invalidate_user_cache(user_id)
    cache_service.invalidate_organization_cache(org_id)
    # Also invalidate common query caches
    cache_service.invalidate_query_cache("calculations")
    cache_service.invalidate_query_cache("projects")
    cache_service.invalidate_query_cache("vessels")


def warm_cache_for_organization(org_id: int):
    """
    Warm up cache with frequently accessed organization data.
    This can be called after organization updates or periodically.
    """
    try:
        from app.crud.organization import organization_crud
        from app.crud.project import project_crud
        from app.crud.user import user_crud
        from app.db.base import get_db
        
        # This would be called from a background task
        # Implementation depends on your specific needs
        logger.info(f"Cache warming initiated for organization {org_id}")
        
    except Exception as e:
        logger.error(f"Cache warming failed for organization {org_id}: {e}")


# Cache configuration for different data types
CACHE_CONFIGS = {
    "calculations": {"ttl": 300, "prefix": "calc"},
    "projects": {"ttl": 600, "prefix": "proj"},
    "vessels": {"ttl": 600, "prefix": "vessel"},
    "users": {"ttl": 900, "prefix": "user"},
    "materials": {"ttl": 3600, "prefix": "material"},  # Materials change less frequently
    "organizations": {"ttl": 1800, "prefix": "org"},
    "dashboard": {"ttl": 300, "prefix": "dashboard"},
    "reports": {"ttl": 1800, "prefix": "report"},
    "inspections": {"ttl": 600, "prefix": "inspection"},
}


def get_cache_config(data_type: str) -> Dict[str, Any]:
    """Get cache configuration for data type."""
    return CACHE_CONFIGS.get(data_type, {"ttl": 300, "prefix": "default"})