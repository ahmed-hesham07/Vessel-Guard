"""
Performance tests for the Vessel Guard application.

Tests for response times, throughput, memory usage,
and database performance under various load conditions.
"""

import pytest
import time
import asyncio
import concurrent.futures
from typing import List, Dict, Any
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.models.user import User
from app.db.models.organization import Organization
from app.db.models.project import Project
from app.services.cache_service import cache_service
from app.services.optimization_service import query_optimizer, db_monitor


class TestAPIPerformance:
    """Test API endpoint performance."""
    
    def test_project_list_performance(self, client: TestClient, auth_headers: dict):
        """Test project list endpoint performance."""
        
        # Warm up
        client.get("/api/v1/projects", headers=auth_headers)
        
        # Measure performance
        start_time = time.time()
        response = client.get("/api/v1/projects?limit=100", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Should respond within 500ms for list operations
        assert response_time < 0.5, f"Response time {response_time:.3f}s exceeded threshold"
        
        # Check response structure
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_project_creation_performance(self, client: TestClient, auth_headers: dict):
        """Test project creation performance."""
        
        project_data = {
            "name": f"Performance Test Project {int(time.time())}",
            "description": "Testing project creation performance",
            "status": "planning"
        }
        
        start_time = time.time()
        response = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 201
        response_time = end_time - start_time
        
        # Should create within 1 second
        assert response_time < 1.0, f"Creation time {response_time:.3f}s exceeded threshold"
    
    def test_concurrent_requests_performance(self, client: TestClient, auth_headers: dict):
        """Test concurrent request handling."""
        
        def make_request():
            response = client.get("/api/v1/projects", headers=auth_headers)
            return response.status_code, time.time()
        
        # Test with 10 concurrent requests
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        assert all(status_code == 200 for status_code, _ in results)
        
        # Should handle 10 concurrent requests within 2 seconds
        assert total_time < 2.0, f"Concurrent requests took {total_time:.3f}s"
        
        # Average response time should be reasonable
        avg_response_time = total_time / len(results)
        assert avg_response_time < 0.2, f"Average response time {avg_response_time:.3f}s too high"


class TestDatabasePerformance:
    """Test database operation performance."""
    
    def test_connection_pool_performance(self, db_session: Session):
        """Test database connection pool performance."""
        
        # Test connection acquisition speed
        start_time = time.time()
        
        for _ in range(50):
            # Simulate database operations
            result = db_session.execute("SELECT 1").scalar()
            assert result == 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 50 simple queries should complete quickly
        assert total_time < 1.0, f"50 queries took {total_time:.3f}s"
    
    def test_query_performance_with_indexes(self, db_session: Session, test_organization: Organization):
        """Test query performance with proper indexes."""
        
        # Test organization-based query performance
        start_time = time.time()
        
        projects = db_session.query(Project).filter(
            Project.organization_id == test_organization.id
        ).limit(100).all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Query should be fast with proper index
        assert query_time < 0.1, f"Indexed query took {query_time:.3f}s"
    
    def test_bulk_insert_performance(self, db_session: Session, test_organization: Organization):
        """Test bulk insert performance."""
        
        # Prepare bulk data
        projects_data = []
        for i in range(100):
            projects_data.append({
                "name": f"Bulk Test Project {i}",
                "description": f"Bulk test project {i}",
                "organization_id": test_organization.id,
                "status": "planning",
                "priority": "medium"
            })
        
        start_time = time.time()
        
        # Use bulk insert
        db_session.bulk_insert_mappings(Project, projects_data)
        db_session.commit()
        
        end_time = time.time()
        insert_time = end_time - start_time
        
        # Bulk insert should be fast
        assert insert_time < 2.0, f"Bulk insert of 100 records took {insert_time:.3f}s"
        
        # Verify records were created
        count = db_session.query(Project).filter(
            Project.name.like("Bulk Test Project%")
        ).count()
        assert count == 100
    
    def test_complex_query_performance(self, db_session: Session, test_organization: Organization):
        """Test complex query performance."""
        
        # Complex query with joins
        start_time = time.time()
        
        query = """
        SELECT p.id, p.name, COUNT(v.id) as vessel_count
        FROM projects p
        LEFT JOIN vessels v ON p.id = v.project_id
        WHERE p.organization_id = :org_id
        GROUP BY p.id, p.name
        ORDER BY vessel_count DESC
        LIMIT 50
        """
        
        result = db_session.execute(query, {"org_id": test_organization.id}).fetchall()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Complex query should still be reasonably fast
        assert query_time < 0.5, f"Complex query took {query_time:.3f}s"


class TestCachePerformance:
    """Test caching system performance."""
    
    def test_cache_hit_performance(self):
        """Test cache hit performance."""
        
        # Set test data
        test_data = {"large_data": list(range(1000))}
        cache_key = "performance_test_key"
        
        cache_service.set(cache_key, test_data, ttl=60)
        
        # Measure cache hit performance
        start_time = time.time()
        
        for _ in range(100):
            cached_data = cache_service.get(cache_key)
            assert cached_data is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 100 cache hits should be very fast
        assert total_time < 0.1, f"100 cache hits took {total_time:.3f}s"
        
        # Clean up
        cache_service.delete(cache_key)
    
    def test_cache_miss_performance(self):
        """Test cache miss handling performance."""
        
        start_time = time.time()
        
        for i in range(100):
            # Each key will be a miss
            result = cache_service.get(f"non_existent_key_{i}")
            assert result is None
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Cache misses should still be fast
        assert total_time < 0.5, f"100 cache misses took {total_time:.3f}s"
    
    def test_cache_invalidation_performance(self):
        """Test cache invalidation performance."""
        
        # Create many cache entries
        for i in range(100):
            cache_service.set(f"test_key_{i}", f"test_data_{i}", ttl=60)
        
        # Measure pattern-based invalidation
        start_time = time.time()
        
        deleted_count = cache_service.delete_pattern("vessel_guard:test_key_*")
        
        end_time = time.time()
        invalidation_time = end_time - start_time
        
        # Pattern-based deletion should be reasonably fast
        assert invalidation_time < 1.0, f"Cache invalidation took {invalidation_time:.3f}s"
        assert deleted_count > 0


class TestMemoryPerformance:
    """Test memory usage and leaks."""
    
    def test_memory_usage_stability(self, client: TestClient, auth_headers: dict):
        """Test that memory usage remains stable under load."""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for i in range(50):
            # Create project
            project_data = {
                "name": f"Memory Test Project {i}",
                "description": "Testing memory usage",
                "status": "planning"
            }
            
            response = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
            assert response.status_code == 201
            
            # Get projects list
            response = client.get("/api/v1/projects", headers=auth_headers)
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB"


class TestLoadScenarios:
    """Test various load scenarios."""
    
    def test_gradual_load_increase(self, client: TestClient, auth_headers: dict):
        """Test system behavior under gradually increasing load."""
        
        response_times = []
        
        for concurrent_users in [1, 5, 10, 15, 20]:
            def make_requests():
                times = []
                for _ in range(5):  # Each user makes 5 requests
                    start = time.time()
                    response = client.get("/api/v1/projects", headers=auth_headers)
                    end = time.time()
                    
                    assert response.status_code == 200
                    times.append(end - start)
                return times
            
            # Simulate concurrent users
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_requests) for _ in range(concurrent_users)]
                all_times = []
                for future in concurrent.futures.as_completed(futures):
                    all_times.extend(future.result())
            
            avg_response_time = sum(all_times) / len(all_times)
            response_times.append((concurrent_users, avg_response_time))
            
            # Response time shouldn't degrade too much
            assert avg_response_time < 2.0, f"Average response time {avg_response_time:.3f}s too high for {concurrent_users} users"
        
        # Log performance characteristics
        for users, avg_time in response_times:
            print(f"Users: {users}, Avg Response Time: {avg_time:.3f}s")
    
    def test_sustained_load(self, client: TestClient, auth_headers: dict):
        """Test system behavior under sustained load."""
        
        duration = 30  # seconds
        start_time = time.time()
        request_count = 0
        error_count = 0
        
        while time.time() - start_time < duration:
            try:
                response = client.get("/api/v1/projects", headers=auth_headers)
                if response.status_code != 200:
                    error_count += 1
                request_count += 1
                
                # Small delay to avoid overwhelming
                time.sleep(0.1)
                
            except Exception:
                error_count += 1
                request_count += 1
        
        error_rate = error_count / request_count if request_count > 0 else 1
        
        # Error rate should be low
        assert error_rate < 0.05, f"Error rate {error_rate:.2%} too high during sustained load"
        
        # Should handle reasonable throughput
        requests_per_second = request_count / duration
        assert requests_per_second > 5, f"Throughput {requests_per_second:.1f} req/s too low"


class TestDatabaseMonitoring:
    """Test database monitoring and optimization features."""
    
    def test_connection_monitoring(self, db_session: Session):
        """Test database connection monitoring."""
        
        stats = db_monitor.get_connection_stats(db_session)
        
        assert isinstance(stats, dict)
        if stats:  # Only test if stats are available
            assert "total_connections" in stats
            assert stats["total_connections"] >= 0
    
    def test_table_size_monitoring(self, db_session: Session):
        """Test table size monitoring."""
        
        table_sizes = db_monitor.get_table_sizes(db_session)
        
        assert isinstance(table_sizes, list)
        if table_sizes:  # Only test if data is available
            for table_info in table_sizes:
                assert "tablename" in table_info
                assert "size" in table_info
    
    def test_slow_query_detection(self, db_session: Session):
        """Test slow query detection."""
        
        # This might not work in test environment, so we'll test gracefully
        slow_queries = query_optimizer.get_slow_queries(db_session, limit=5)
        
        assert isinstance(slow_queries, list)
        # In test environment, this might be empty, which is fine
    
    def test_query_explanation(self, db_session: Session):
        """Test query explanation functionality."""
        
        simple_query = "SELECT COUNT(*) FROM projects"
        explanation = query_optimizer.explain_query(db_session, simple_query)
        
        assert isinstance(explanation, dict)
        assert "status" in explanation
        
        if explanation["status"] == "success":
            assert "plan" in explanation
        else:
            assert "error" in explanation


@pytest.mark.performance
class TestBenchmarks:
    """Benchmark tests for specific operations."""
    
    def test_project_crud_benchmark(self, client: TestClient, auth_headers: dict):
        """Benchmark CRUD operations for projects."""
        
        # Create benchmark
        create_times = []
        for i in range(10):
            project_data = {
                "name": f"Benchmark Project {i}",
                "description": "Benchmark test project",
                "status": "planning"
            }
            
            start = time.time()
            response = client.post("/api/v1/projects", json=project_data, headers=auth_headers)
            end = time.time()
            
            assert response.status_code == 201
            create_times.append(end - start)
        
        avg_create_time = sum(create_times) / len(create_times)
        
        # Read benchmark
        start = time.time()
        response = client.get("/api/v1/projects", headers=auth_headers)
        end = time.time()
        
        assert response.status_code == 200
        read_time = end - start
        
        # Log benchmark results
        print(f"Average project creation time: {avg_create_time:.3f}s")
        print(f"Project list read time: {read_time:.3f}s")
        
        # Set performance expectations
        assert avg_create_time < 0.5, f"Average creation time {avg_create_time:.3f}s too slow"
        assert read_time < 0.2, f"Read time {read_time:.3f}s too slow"