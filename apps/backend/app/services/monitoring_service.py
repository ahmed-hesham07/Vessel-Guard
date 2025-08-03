"""
Comprehensive monitoring service for the Vessel Guard application.

Provides application metrics, health monitoring, performance tracking,
and alerting capabilities for production deployment.
"""

import time
import psutil
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.cache_service import cache_service
from app.db.base import get_db

logger = get_logger(__name__)


@dataclass
class SystemMetrics:
    """System-level metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    load_average_1m: float
    active_connections: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ApplicationMetrics:
    """Application-level metrics."""
    timestamp: datetime
    total_users: int
    active_users_24h: int
    total_projects: int
    active_projects: int
    total_calculations: int
    calculations_24h: int
    failed_calculations_24h: int
    total_reports: int
    reports_generated_24h: int
    cache_hit_rate: float
    average_response_time: float
    error_rate_24h: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class DatabaseMetrics:
    """Database-level metrics."""
    timestamp: datetime
    total_connections: int
    active_connections: int
    idle_connections: int
    slow_queries_count: int
    database_size_mb: float
    largest_table_mb: float
    index_hit_ratio: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class MetricsCollector:
    """Collects various application and system metrics."""
    
    def __init__(self):
        self.logger = get_logger('vessel_guard.monitoring.metrics')
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024 ** 3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            disk_free_gb = disk.free / (1024 ** 3)
            
            # Load average (Unix-like systems)
            try:
                load_average_1m = psutil.getloadavg()[0]
            except (AttributeError, OSError):
                load_average_1m = 0.0  # Not available on Windows
            
            # Network connections
            connections = psutil.net_connections()
            active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                load_average_1m=load_average_1m,
                active_connections=active_connections
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            # Return default metrics on error
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_gb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                load_average_1m=0.0,
                active_connections=0
            )
    
    def collect_application_metrics(self, db: Session) -> ApplicationMetrics:
        """Collect application-level metrics."""
        try:
            from app.db.models.user import User
            from app.db.models.project import Project
            from app.db.models.calculation import Calculation
            from app.db.models.report import Report
            
            now = datetime.utcnow()
            yesterday = now - timedelta(days=1)
            
            # User metrics
            total_users = db.query(User).filter(User.is_active == True).count()
            active_users_24h = db.query(User).filter(
                User.last_login >= yesterday,
                User.is_active == True
            ).count()
            
            # Project metrics
            total_projects = db.query(Project).filter(Project.is_active == True).count()
            active_projects = db.query(Project).filter(
                Project.status.in_(['planning', 'active']),
                Project.is_active == True
            ).count()
            
            # Calculation metrics
            total_calculations = db.query(Calculation).filter(Calculation.is_active == True).count()
            calculations_24h = db.query(Calculation).filter(
                Calculation.created_at >= yesterday,
                Calculation.is_active == True
            ).count()
            failed_calculations_24h = db.query(Calculation).filter(
                Calculation.created_at >= yesterday,
                Calculation.status == 'failed',
                Calculation.is_active == True
            ).count()
            
            # Report metrics
            total_reports = db.query(Report).filter(Report.is_active == True).count()
            reports_generated_24h = db.query(Report).filter(
                Report.created_at >= yesterday,
                Report.is_active == True
            ).count()
            
            # Calculate error rate
            if calculations_24h > 0:
                error_rate_24h = (failed_calculations_24h / calculations_24h) * 100
            else:
                error_rate_24h = 0.0
            
            # Cache metrics (if available)
            cache_hit_rate = self._get_cache_hit_rate()
            
            # Performance metrics
            average_response_time = self._get_average_response_time()
            
            return ApplicationMetrics(
                timestamp=now,
                total_users=total_users,
                active_users_24h=active_users_24h,
                total_projects=total_projects,
                active_projects=active_projects,
                total_calculations=total_calculations,
                calculations_24h=calculations_24h,
                failed_calculations_24h=failed_calculations_24h,
                total_reports=total_reports,
                reports_generated_24h=reports_generated_24h,
                cache_hit_rate=cache_hit_rate,
                average_response_time=average_response_time,
                error_rate_24h=error_rate_24h
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect application metrics: {e}")
            # Return default metrics on error
            now = datetime.utcnow()
            return ApplicationMetrics(
                timestamp=now,
                total_users=0,
                active_users_24h=0,
                total_projects=0,
                active_projects=0,
                total_calculations=0,
                calculations_24h=0,
                failed_calculations_24h=0,
                total_reports=0,
                reports_generated_24h=0,
                cache_hit_rate=0.0,
                average_response_time=0.0,
                error_rate_24h=0.0
            )
    
    def collect_database_metrics(self, db: Session) -> DatabaseMetrics:
        """Collect database-level metrics."""
        try:
            # Connection metrics
            connection_stats = self._get_connection_stats(db)
            
            # Database size
            database_size_mb = self._get_database_size(db)
            largest_table_mb = self._get_largest_table_size(db)
            
            # Performance metrics
            slow_queries_count = self._get_slow_queries_count(db)
            index_hit_ratio = self._get_index_hit_ratio(db)
            
            return DatabaseMetrics(
                timestamp=datetime.utcnow(),
                total_connections=connection_stats.get('total_connections', 0),
                active_connections=connection_stats.get('active_connections', 0),
                idle_connections=connection_stats.get('idle_connections', 0),
                slow_queries_count=slow_queries_count,
                database_size_mb=database_size_mb,
                largest_table_mb=largest_table_mb,
                index_hit_ratio=index_hit_ratio
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect database metrics: {e}")
            return DatabaseMetrics(
                timestamp=datetime.utcnow(),
                total_connections=0,
                active_connections=0,
                idle_connections=0,
                slow_queries_count=0,
                database_size_mb=0.0,
                largest_table_mb=0.0,
                index_hit_ratio=0.0
            )
    
    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate from monitoring data."""
        try:
            # This would be implemented based on your cache monitoring
            # For now, return a placeholder
            return 95.0  # Assume 95% hit rate
        except Exception:
            return 0.0
    
    def _get_average_response_time(self) -> float:
        """Get average response time from performance monitoring."""
        try:
            # This would be implemented based on your performance monitoring
            # For now, return a placeholder
            return 0.15  # Assume 150ms average
        except Exception:
            return 0.0
    
    def _get_connection_stats(self, db: Session) -> Dict[str, int]:
        """Get database connection statistics."""
        try:
            query = """
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections
            FROM pg_stat_activity 
            WHERE datname = current_database()
            """
            result = db.execute(text(query)).fetchone()
            return dict(result) if result else {}
        except Exception:
            return {}
    
    def _get_database_size(self, db: Session) -> float:
        """Get database size in MB."""
        try:
            query = "SELECT pg_database_size(current_database()) / 1024.0 / 1024.0 as size_mb"
            result = db.execute(text(query)).scalar()
            return float(result) if result else 0.0
        except Exception:
            return 0.0
    
    def _get_largest_table_size(self, db: Session) -> float:
        """Get largest table size in MB."""
        try:
            query = """
            SELECT pg_total_relation_size(schemaname||'.'||tablename) / 1024.0 / 1024.0 as size_mb
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 1
            """
            result = db.execute(text(query)).scalar()
            return float(result) if result else 0.0
        except Exception:
            return 0.0
    
    def _get_slow_queries_count(self, db: Session) -> int:
        """Get count of slow queries."""
        try:
            # This requires pg_stat_statements extension
            query = """
            SELECT count(*) 
            FROM pg_stat_statements 
            WHERE mean_time > 1000
            """
            result = db.execute(text(query)).scalar()
            return int(result) if result else 0
        except Exception:
            return 0
    
    def _get_index_hit_ratio(self, db: Session) -> float:
        """Get index hit ratio."""
        try:
            query = """
            SELECT 
                100.0 * sum(idx_blks_hit) / nullif(sum(idx_blks_hit + idx_blks_read), 0) as ratio
            FROM pg_statio_user_indexes
            """
            result = db.execute(text(query)).scalar()
            return float(result) if result else 0.0
        except Exception:
            return 0.0


class HealthChecker:
    """Performs comprehensive health checks."""
    
    def __init__(self):
        self.logger = get_logger('vessel_guard.monitoring.health')
    
    def check_application_health(self) -> Dict[str, Any]:
        """Perform comprehensive application health check."""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Database health
        db_health = self._check_database_health()
        health_status['checks']['database'] = db_health
        
        # Cache health
        cache_health = self._check_cache_health()
        health_status['checks']['cache'] = cache_health
        
        # System resources health
        system_health = self._check_system_resources()
        health_status['checks']['system'] = system_health
        
        # External services health
        external_health = self._check_external_services()
        health_status['checks']['external'] = external_health
        
        # Determine overall status
        failed_checks = [name for name, check in health_status['checks'].items() 
                        if check['status'] != 'healthy']
        
        if failed_checks:
            if len(failed_checks) == 1 and failed_checks[0] in ['cache', 'external']:
                health_status['overall_status'] = 'degraded'
            else:
                health_status['overall_status'] = 'unhealthy'
            
            health_status['failed_checks'] = failed_checks
        
        return health_status
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            db = next(get_db())
            start_time = time.time()
            
            # Test basic query
            result = db.execute(text("SELECT 1")).scalar()
            
            # Test table access
            db.execute(text("SELECT COUNT(*) FROM users LIMIT 1")).scalar()
            
            query_time = time.time() - start_time
            
            db.close()
            
            if result == 1 and query_time < 1.0:  # Should respond within 1 second
                return {
                    'status': 'healthy',
                    'response_time': query_time,
                    'message': 'Database is responsive'
                }
            else:
                return {
                    'status': 'degraded',
                    'response_time': query_time,
                    'message': 'Database is slow to respond'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Database connection failed'
            }
    
    def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache service health."""
        try:
            start_time = time.time()
            
            # Test cache operations
            test_key = "health_check_test"
            test_value = {"test": "data", "timestamp": time.time()}
            
            # Set operation
            set_success = cache_service.set(test_key, test_value, ttl=10)
            
            # Get operation
            retrieved_value = cache_service.get(test_key)
            
            # Clean up
            cache_service.delete(test_key)
            
            operation_time = time.time() - start_time
            
            if set_success and retrieved_value == test_value and operation_time < 0.1:
                return {
                    'status': 'healthy',
                    'response_time': operation_time,
                    'message': 'Cache is operational'
                }
            else:
                return {
                    'status': 'degraded',
                    'response_time': operation_time,
                    'message': 'Cache operations are slow or failing'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Cache service is not available'
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource availability."""
        try:
            # Memory check
            memory = psutil.virtual_memory()
            
            # Disk check
            disk = psutil.disk_usage('/')
            
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            
            issues = []
            
            if memory.percent > 90:
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 90:
                issues.append(f"High disk usage: {disk.percent:.1f}%")
            
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if issues:
                return {
                    'status': 'degraded',
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'cpu_percent': cpu_percent,
                    'issues': issues,
                    'message': 'High resource usage detected'
                }
            else:
                return {
                    'status': 'healthy',
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'cpu_percent': cpu_percent,
                    'message': 'System resources are within normal limits'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Unable to check system resources'
            }
    
    def _check_external_services(self) -> Dict[str, Any]:
        """Check external service dependencies."""
        try:
            # This would check external APIs, SMTP servers, etc.
            # For now, return healthy as we don't have external dependencies
            return {
                'status': 'healthy',
                'message': 'No external service dependencies to check'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'External service check failed'
            }


class AlertManager:
    """Manages alerts and notifications for monitoring."""
    
    def __init__(self):
        self.logger = get_logger('vessel_guard.monitoring.alerts')
        self.alert_thresholds = {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0,
            'error_rate_threshold': 10.0,  # 10% error rate
            'response_time_threshold': 2.0,  # 2 seconds
            'failed_calculations_threshold': 50  # 50 failed calculations per day
        }
    
    def check_alerts(self, system_metrics: SystemMetrics, 
                    app_metrics: ApplicationMetrics,
                    db_metrics: DatabaseMetrics) -> List[Dict[str, Any]]:
        """Check for alert conditions."""
        alerts = []
        
        # System alerts
        if system_metrics.cpu_percent > self.alert_thresholds['cpu_threshold']:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'metric': 'cpu_usage',
                'value': system_metrics.cpu_percent,
                'threshold': self.alert_thresholds['cpu_threshold'],
                'message': f"High CPU usage: {system_metrics.cpu_percent:.1f}%"
            })
        
        if system_metrics.memory_percent > self.alert_thresholds['memory_threshold']:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'metric': 'memory_usage',
                'value': system_metrics.memory_percent,
                'threshold': self.alert_thresholds['memory_threshold'],
                'message': f"High memory usage: {system_metrics.memory_percent:.1f}%"
            })
        
        if system_metrics.disk_usage_percent > self.alert_thresholds['disk_threshold']:
            alerts.append({
                'type': 'system',
                'severity': 'critical',
                'metric': 'disk_usage',
                'value': system_metrics.disk_usage_percent,
                'threshold': self.alert_thresholds['disk_threshold'],
                'message': f"High disk usage: {system_metrics.disk_usage_percent:.1f}%"
            })
        
        # Application alerts
        if app_metrics.error_rate_24h > self.alert_thresholds['error_rate_threshold']:
            alerts.append({
                'type': 'application',
                'severity': 'warning',
                'metric': 'error_rate',
                'value': app_metrics.error_rate_24h,
                'threshold': self.alert_thresholds['error_rate_threshold'],
                'message': f"High error rate: {app_metrics.error_rate_24h:.1f}%"
            })
        
        if app_metrics.average_response_time > self.alert_thresholds['response_time_threshold']:
            alerts.append({
                'type': 'application',
                'severity': 'warning',
                'metric': 'response_time',
                'value': app_metrics.average_response_time,
                'threshold': self.alert_thresholds['response_time_threshold'],
                'message': f"High response time: {app_metrics.average_response_time:.2f}s"
            })
        
        if app_metrics.failed_calculations_24h > self.alert_thresholds['failed_calculations_threshold']:
            alerts.append({
                'type': 'application',
                'severity': 'warning',
                'metric': 'failed_calculations',
                'value': app_metrics.failed_calculations_24h,
                'threshold': self.alert_thresholds['failed_calculations_threshold'],
                'message': f"High number of failed calculations: {app_metrics.failed_calculations_24h}"
            })
        
        return alerts
    
    def send_alert(self, alert: Dict[str, Any]):
        """Send alert notification."""
        try:
            # Log the alert
            self.logger.warning(f"ALERT [{alert['severity'].upper()}]: {alert['message']}")
            
            # In a real implementation, you would send this to:
            # - Email notifications
            # - Slack/Teams webhooks
            # - PagerDuty/OpsGenie
            # - Monitoring systems (Datadog, New Relic, etc.)
            
            # For now, just store in cache for retrieval
            alert_key = f"alert:{int(time.time())}"
            cache_service.set(alert_key, alert, ttl=3600)  # Store for 1 hour
            
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")


# Global monitoring instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()
alert_manager = AlertManager()


def collect_all_metrics() -> Dict[str, Any]:
    """Collect all metrics in one operation."""
    try:
        db = next(get_db())
        
        system_metrics = metrics_collector.collect_system_metrics()
        app_metrics = metrics_collector.collect_application_metrics(db)
        db_metrics = metrics_collector.collect_database_metrics(db)
        
        db.close()
        
        # Check for alerts
        alerts = alert_manager.check_alerts(system_metrics, app_metrics, db_metrics)
        
        # Send any critical alerts
        for alert in alerts:
            if alert['severity'] in ['critical', 'warning']:
                alert_manager.send_alert(alert)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': system_metrics.to_dict(),
            'application': app_metrics.to_dict(),
            'database': db_metrics.to_dict(),
            'alerts': alerts
        }
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'status': 'collection_failed'
        }