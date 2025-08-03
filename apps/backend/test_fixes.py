#!/usr/bin/env python3
"""
Test script to verify that all critical errors have been fixed.
"""

import sys
import traceback
from typing import List, Dict, Any

def test_import_main_app() -> bool:
    """Test that the main app can be imported without errors."""
    try:
        from app.main import app
        print("✅ Main app imports successfully")
        return True
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        traceback.print_exc()
        return False

def test_config_environment() -> bool:
    """Test that ENVIRONMENT configuration is available."""
    try:
        from app.core.config import settings
        env = settings.ENVIRONMENT
        print(f"✅ ENVIRONMENT setting available: {env}")
        return True
    except AttributeError as e:
        print(f"❌ ENVIRONMENT setting missing: {e}")
        return False
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_database_connection() -> bool:
    """Test that database connection works."""
    try:
        from app.db.connection import test_database_connection
        from app.db.base import engine
        
        result = test_database_connection(engine)
        if result:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_calculations_syntax() -> bool:
    """Test that calculations module has correct syntax."""
    try:
        import app.api.v1.endpoints.calculations
        print("✅ Calculations module syntax is correct")
        return True
    except SyntaxError as e:
        print(f"❌ Calculations module syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Calculations module import error: {e}")
        return False

def test_role_hierarchy() -> bool:
    """Test that role hierarchy function can handle different input types."""
    try:
        from app.api.dependencies import require_role
        from app.db.models.user import UserRole
        
        # Test with single role
        single_role_dep = require_role(UserRole.ENGINEER)
        print("✅ Single role dependency created successfully")
        
        # Test with list of roles
        list_role_dep = require_role([UserRole.CONSULTANT, UserRole.ENGINEER])
        print("✅ List role dependency created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Role hierarchy test failed: {e}")
        traceback.print_exc()
        return False

def test_health_endpoint() -> bool:
    """Test that health endpoint configuration is correct."""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ Health endpoint responds correctly")
            data = response.json()
            if "status" in data and "app_name" in data:
                print("✅ Health endpoint returns correct data structure")
                return True
            else:
                print("❌ Health endpoint missing expected fields")
                return False
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def run_all_tests() -> Dict[str, bool]:
    """Run all tests and return results."""
    tests = {
        "Main App Import": test_import_main_app,
        "Environment Config": test_config_environment,
        "Database Connection": test_database_connection,
        "Calculations Syntax": test_calculations_syntax,
        "Role Hierarchy": test_role_hierarchy,
        "Health Endpoint": test_health_endpoint,
    }
    
    results = {}
    print("🔍 Running critical error fix tests...\n")
    
    for test_name, test_func in tests.items():
        print(f"Running: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
        print()
    
    return results

def main():
    """Main test runner."""
    results = run_all_tests()
    
    # Summary
    print("=" * 50)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All critical errors have been fixed!")
        sys.exit(0)
    else:
        print("⚠️  Some issues remain to be addressed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
