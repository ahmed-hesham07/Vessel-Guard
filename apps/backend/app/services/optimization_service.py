"""
API optimization service for improving endpoint performance.

Provides query optimization, bulk operations, and performance
monitoring for API endpoints.
"""

import time
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.logging_config import get_logger
from app.services.cache_service import cache_service

logger = get_logger(__name__)


class QueryOptimizer:
    """
    Query optimization utilities for improving database performance.
    """
    
    @staticmethod
    def explain_query(db: Session, query_sql: str) -> Dict[str, Any]:
        """
        Explain a SQL query to analyze performance.
        
        Args:
            db: Database session
            query_sql: SQL query to explain
            
        Returns:
            Query execution plan
        """
        try:
            explain_result = db.execute(text(f"EXPLAIN ANALYZE {query_sql}")).fetchall()
            return {
                "query": query_sql,
                "plan": [dict(row) for row in explain_result],
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Query explain failed: {e}")
            return {
                "query": query_sql,
                "error": str(e),
                "status": "error"
            }
    
    @staticmethod
    def get_slow_queries(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get slow queries from PostgreSQL statistics.
        
        Args:
            db: Database session
            limit: Number of queries to return
            
        Returns:
            List of slow queries with statistics
        """
        try:
            slow_query_sql = """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                max_time,
                rows,
                100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
            FROM pg_stat_statements 
            WHERE query NOT LIKE '%pg_stat_statements%'
            ORDER BY total_time DESC 
            LIMIT :limit
            """
            
            result = db.execute(text(slow_query_sql), {"limit": limit}).fetchall()
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get slow queries: {e}")
            return []
    
    @staticmethod
    def optimize_bulk_insert(db: Session, model_class, records: List[Dict], batch_size: int = 1000):
        """
        Optimized bulk insert for large datasets.
        
        Args:
            db: Database session
            model_class: SQLAlchemy model class
            records: List of record dictionaries
            batch_size: Number of records per batch
        """
        try:
            total_records = len(records)
            batches = [records[i:i + batch_size] for i in range(0, total_records, batch_size)]
            
            for i, batch in enumerate(batches):
                db.bulk_insert_mappings(model_class, batch)
                db.commit()
                logger.info(f"Inserted batch {i+1}/{len(batches)} ({len(batch)} records)")
            
            logger.info(f"Bulk insert completed: {total_records} records")
            return True
            
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            db.rollback()
            return False


def performance_monitor(operation_name: str, log_slow_threshold: float = 1.0):
    """
    Decorator to monitor API endpoint performance.
    
    Args:
        operation_name: Name of the operation for logging
        log_slow_threshold: Threshold in seconds to log slow operations
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > log_slow_threshold:
                    logger.warning(
                        f"Slow operation detected: {operation_name} took {execution_time:.3f}s",
                        extra={
                            "operation": operation_name,
                            "execution_time": execution_time,
                            "threshold": log_slow_threshold
                        }
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Operation failed: {operation_name} after {execution_time:.3f}s",
                    extra={
                        "operation": operation_name,
                        "execution_time": execution_time,
                        "error": str(e)
                    }
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > log_slow_threshold:
                    logger.warning(
                        f"Slow operation detected: {operation_name} took {execution_time:.3f}s",
                        extra={
                            "operation": operation_name,
                            "execution_time": execution_time,
                            "threshold": log_slow_threshold
                        }
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Operation failed: {operation_name} after {execution_time:.3f}s",
                    extra={
                        "operation": operation_name,
                        "execution_time": execution_time,
                        "error": str(e)
                    }
                )
                raise
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class BulkOperationService:
    """
    Service for handling bulk operations efficiently.
    """
    
    @staticmethod
    def bulk_create_calculations(
        db: Session, 
        calculations_data: List[Dict[str, Any]], 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Bulk create calculations with optimization.
        
        Args:
            db: Database session
            calculations_data: List of calculation data
            user_id: User performing the operation
            
        Returns:
            Operation result with statistics
        """
        try:
            start_time = time.time()
            
            # Add user_id and timestamps to all records
            for calc_data in calculations_data:
                calc_data['calculated_by_id'] = user_id
                calc_data['created_at'] = time.time()
                calc_data['updated_at'] = time.time()
            
            # Use bulk insert for better performance
            from app.db.models.calculation import Calculation
            db.bulk_insert_mappings(Calculation, calculations_data)
            db.commit()
            
            execution_time = time.time() - start_time
            
            # Invalidate related caches
            cache_service.invalidate_query_cache("calculations")
            cache_service.invalidate_query_cache("recent_calculations")
            
            result = {
                "status": "success",
                "records_created": len(calculations_data),
                "execution_time": execution_time,
                "average_time_per_record": execution_time / len(calculations_data)
            }
            
            logger.info(
                f"Bulk calculation creation completed",
                extra=result
            )
            
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk calculation creation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "records_attempted": len(calculations_data)
            }
    
    @staticmethod
    def bulk_update_calculation_status(
        db: Session,
        calculation_ids: List[int],
        new_status: str
    ) -> Dict[str, Any]:
        """
        Bulk update calculation status.
        
        Args:
            db: Database session
            calculation_ids: List of calculation IDs
            new_status: New status to set
            
        Returns:
            Operation result
        """
        try:
            from app.db.models.calculation import Calculation
            
            updated_count = db.query(Calculation).filter(
                Calculation.id.in_(calculation_ids)
            ).update(
                {"status": new_status, "updated_at": time.time()},
                synchronize_session=False
            )
            
            db.commit()
            
            # Invalidate related caches
            cache_service.invalidate_query_cache("calculations")
            
            return {
                "status": "success",
                "records_updated": updated_count
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk status update failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class DatabaseHealthMonitor:
    """
    Monitor database health and performance metrics.
    """
    
    @staticmethod
    def get_connection_stats(db: Session) -> Dict[str, Any]:
        """Get database connection statistics."""
        try:
            stats_query = """
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
            FROM pg_stat_activity 
            WHERE datname = current_database()
            """
            
            result = db.execute(text(stats_query)).fetchone()
            return dict(result) if result else {}
            
        except Exception as e:
            logger.error(f"Failed to get connection stats: {e}")
            return {}
    
    @staticmethod
    def get_table_sizes(db: Session) -> List[Dict[str, Any]]:
        """Get table sizes for monitoring."""
        try:
            size_query = """
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """
            
            result = db.execute(text(size_query)).fetchall()
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get table sizes: {e}")
            return []


# Global optimization service instance
optimization_service = BulkOperationService()
query_optimizer = QueryOptimizer()
db_monitor = DatabaseHealthMonitor()