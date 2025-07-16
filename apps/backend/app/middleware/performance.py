"""
Performance monitoring middleware for request tracking and metrics collection.
"""

import time
import asyncio
import psutil
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging_config import get_logger, log_performance, log_api_request


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    
    # Request metrics
    request_count: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    
    # Status code counts
    status_codes: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    
    # Recent response times (for percentile calculations)
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Error tracking
    error_count: int = 0
    error_rate: float = 0.0
    
    def add_request(self, response_time: float, status_code: int):
        """Add a request to metrics."""
        self.request_count += 1
        self.total_response_time += response_time
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
        
        self.status_codes[status_code] += 1
        self.recent_response_times.append(response_time)
        
        if status_code >= 400:
            self.error_count += 1
        
        # Update error rate
        self.error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0.0
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        return self.total_response_time / self.request_count if self.request_count > 0 else 0.0
    
    def get_percentile(self, percentile: float) -> float:
        """Calculate response time percentile."""
        if not self.recent_response_times:
            return 0.0
        
        sorted_times = sorted(self.recent_response_times)
        index = int((percentile / 100) * len(sorted_times))
        index = min(index, len(sorted_times) - 1)
        
        return sorted_times[index]


class SystemMetrics:
    """System resource metrics collector."""
    
    def __init__(self):
        self.logger = get_logger('vessel_guard.performance.system')
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            self.logger.error(f"Failed to get CPU usage: {e}")
            return 0.0
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage information."""
        try:
            memory = psutil.virtual_memory()
            return {
                'total_gb': memory.total / (1024 ** 3),
                'available_gb': memory.available / (1024 ** 3),
                'used_gb': memory.used / (1024 ** 3),
                'usage_percent': memory.percent
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return {'total_gb': 0, 'available_gb': 0, 'used_gb': 0, 'usage_percent': 0}
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage information."""
        try:
            disk = psutil.disk_usage('/')
            return {
                'total_gb': disk.total / (1024 ** 3),
                'free_gb': disk.free / (1024 ** 3),
                'used_gb': disk.used / (1024 ** 3),
                'usage_percent': (disk.used / disk.total) * 100
            }
        except Exception as e:
            self.logger.error(f"Failed to get disk usage: {e}")
            return {'total_gb': 0, 'free_gb': 0, 'used_gb': 0, 'usage_percent': 0}
    
    def get_process_info(self) -> Dict[str, float]:
        """Get current process information."""
        try:
            process = psutil.Process()
            with process.oneshot():
                return {
                    'cpu_percent': process.cpu_percent(),
                    'memory_mb': process.memory_info().rss / (1024 ** 2),
                    'memory_percent': process.memory_percent(),
                    'num_threads': process.num_threads(),
                    'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
                }
        except Exception as e:
            self.logger.error(f"Failed to get process info: {e}")
            return {'cpu_percent': 0, 'memory_mb': 0, 'memory_percent': 0, 'num_threads': 0, 'num_fds': 0}


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Performance monitoring middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger('vessel_guard.performance.middleware')
        
        # Metrics storage
        self.global_metrics = PerformanceMetrics()
        self.endpoint_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        
        # System metrics
        self.system_metrics = SystemMetrics()
        
        # Configuration
        self.enable_detailed_logging = getattr(settings, 'ENABLE_PERFORMANCE_LOGGING', True)
        self.slow_request_threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD_MS', 1000)
        self.log_sample_rate = getattr(settings, 'PERFORMANCE_LOG_SAMPLE_RATE', 0.1)  # Log 10% of requests
        
        # Background task for periodic metrics logging
        # self._start_metrics_task()  # Commented out to avoid event loop issues
    
    def _start_metrics_task(self):
        """Start background task for periodic metrics logging."""
        async def log_metrics_periodically():
            while True:
                await asyncio.sleep(60)  # Log metrics every minute
                self._log_metrics_summary()
        
        # Note: In a real application, you'd want to manage this task lifecycle properly
        asyncio.create_task(log_metrics_periodically())
    
    def _log_metrics_summary(self):
        """Log performance metrics summary."""
        try:
            # System metrics
            cpu_usage = self.system_metrics.get_cpu_usage()
            memory_usage = self.system_metrics.get_memory_usage()
            disk_usage = self.system_metrics.get_disk_usage()
            process_info = self.system_metrics.get_process_info()
            
            # Application metrics
            global_metrics = self.global_metrics
            
            self.logger.info(
                "Performance metrics summary",
                extra={
                    'metrics_type': 'performance_summary',
                    'request_count': global_metrics.request_count,
                    'avg_response_time_ms': global_metrics.avg_response_time,
                    'min_response_time_ms': global_metrics.min_response_time if global_metrics.min_response_time != float('inf') else 0,
                    'max_response_time_ms': global_metrics.max_response_time,
                    'p50_response_time_ms': global_metrics.get_percentile(50),
                    'p95_response_time_ms': global_metrics.get_percentile(95),
                    'p99_response_time_ms': global_metrics.get_percentile(99),
                    'error_rate_percent': global_metrics.error_rate,
                    'status_codes': dict(global_metrics.status_codes),
                    'cpu_usage_percent': cpu_usage,
                    'memory_usage_percent': memory_usage['usage_percent'],
                    'disk_usage_percent': disk_usage['usage_percent'],
                    'process_memory_mb': process_info['memory_mb'],
                    'process_threads': process_info['num_threads']
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log metrics summary: {e}")
    
    def _get_endpoint_key(self, request: Request) -> str:
        """Generate endpoint key for metrics grouping."""
        # Group by method and path pattern (remove IDs)
        path = request.url.path
        method = request.method
        
        # Replace numeric IDs with placeholder
        import re
        path = re.sub(r'/\d+(?=/|$)', '/{id}', path)
        path = re.sub(r'/[a-f0-9-]{36}(?=/|$)', '/{uuid}', path)  # UUIDs
        
        return f"{method} {path}"
    
    def _should_log_request(self) -> bool:
        """Determine if request should be logged based on sample rate."""
        import random
        return random.random() < self.log_sample_rate
    
    def _categorize_response_time(self, response_time_ms: float) -> str:
        """Categorize response time for monitoring."""
        if response_time_ms < 100:
            return 'fast'
        elif response_time_ms < 500:
            return 'normal'
        elif response_time_ms < 1000:
            return 'slow'
        else:
            return 'very_slow'
    
    async def dispatch(self, request: Request, call_next):
        """Process request with performance monitoring."""
        # Skip monitoring for health checks to avoid noise
        if request.url.path.startswith('/health'):
            return await call_next(request)
        
        start_time = time.time()
        
        # Get request context
        endpoint_key = self._get_endpoint_key(request)
        client_ip = request.headers.get('X-Forwarded-For', request.client.host if request.client else 'unknown')
        user_agent = request.headers.get('User-Agent', '')[:100]  # Truncate
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            status_code = response.status_code
            
            # Update metrics
            self.global_metrics.add_request(response_time_ms, status_code)
            self.endpoint_metrics[endpoint_key].add_request(response_time_ms, status_code)
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{response_time_ms:.2f}ms"
            response.headers['X-Request-ID'] = getattr(request.state, 'request_id', 'unknown')
            
            # Log performance data
            if self.enable_detailed_logging:
                # Always log slow requests
                is_slow = response_time_ms > self.slow_request_threshold
                should_log = is_slow or self._should_log_request()
                
                if should_log:
                    log_api_request(
                        method=request.method,
                        path=request.url.path,
                        status_code=status_code,
                        duration_ms=response_time_ms,
                        client_ip=client_ip,
                        user_agent=user_agent,
                        endpoint_key=endpoint_key,
                        response_category=self._categorize_response_time(response_time_ms),
                        is_slow_request=is_slow
                    )
                
                # Log very slow requests with extra detail
                if response_time_ms > self.slow_request_threshold * 2:
                    self.logger.warning(
                        f"Very slow request detected: {endpoint_key}",
                        extra={
                            'response_time_ms': response_time_ms,
                            'threshold_ms': self.slow_request_threshold,
                            'client_ip': client_ip,
                            'user_agent': user_agent,
                            'query_params': dict(request.query_params),
                            'slow_request_alert': True
                        }
                    )
            
            return response
            
        except Exception as e:
            # Handle errors
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Update error metrics
            self.global_metrics.add_request(response_time_ms, 500)
            self.endpoint_metrics[endpoint_key].add_request(response_time_ms, 500)
            
            # Log error with performance context
            self.logger.error(
                f"Request failed: {endpoint_key}",
                extra={
                    'error': str(e),
                    'response_time_ms': response_time_ms,
                    'client_ip': client_ip,
                    'error_during_request': True
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise
    
    def get_metrics_summary(self) -> Dict:
        """Get current metrics summary."""
        try:
            return {
                'global_metrics': {
                    'request_count': self.global_metrics.request_count,
                    'avg_response_time_ms': self.global_metrics.avg_response_time,
                    'min_response_time_ms': self.global_metrics.min_response_time if self.global_metrics.min_response_time != float('inf') else 0,
                    'max_response_time_ms': self.global_metrics.max_response_time,
                    'p50_response_time_ms': self.global_metrics.get_percentile(50),
                    'p95_response_time_ms': self.global_metrics.get_percentile(95),
                    'p99_response_time_ms': self.global_metrics.get_percentile(99),
                    'error_rate_percent': self.global_metrics.error_rate,
                    'status_codes': dict(self.global_metrics.status_codes)
                },
                'system_metrics': {
                    'cpu_usage_percent': self.system_metrics.get_cpu_usage(),
                    **self.system_metrics.get_memory_usage(),
                    **self.system_metrics.get_disk_usage(),
                    **self.system_metrics.get_process_info()
                },
                'top_endpoints': self._get_top_endpoints()
            }
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {e}")
            return {}
    
    def _get_top_endpoints(self, limit: int = 10) -> List[Dict]:
        """Get top endpoints by request count."""
        try:
            sorted_endpoints = sorted(
                self.endpoint_metrics.items(),
                key=lambda x: x[1].request_count,
                reverse=True
            )
            
            return [
                {
                    'endpoint': endpoint,
                    'request_count': metrics.request_count,
                    'avg_response_time_ms': metrics.avg_response_time,
                    'error_rate_percent': metrics.error_rate,
                    'p95_response_time_ms': metrics.get_percentile(95)
                }
                for endpoint, metrics in sorted_endpoints[:limit]
            ]
        except Exception as e:
            self.logger.error(f"Failed to get top endpoints: {e}")
            return []


# Global performance middleware instance for accessing metrics
performance_middleware_instance: Optional[PerformanceMiddleware] = None


def get_performance_metrics() -> Dict:
    """Get current performance metrics."""
    if performance_middleware_instance:
        return performance_middleware_instance.get_metrics_summary()
    return {}


def record_custom_metric(name: str, value: float, **tags):
    """Record a custom performance metric."""
    logger = get_logger('vessel_guard.performance.custom')
    logger.info(
        f"Custom metric: {name}",
        extra={
            'metric_name': name,
            'metric_value': value,
            'custom_metric': True,
            **tags
        }
    )
