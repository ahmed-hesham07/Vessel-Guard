#!/usr/bin/env python3
"""
Simple health endpoint test.
"""

def test_health_endpoint():
    try:
        from app.main import app
        print(f"✅ App created: {app.title}")
        
        # Test that the health endpoint exists
        routes = [route.path for route in app.routes]
        if "/health" in routes:
            print("✅ Health endpoint route exists")
            return True
        else:
            print("❌ Health endpoint route missing")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_health_endpoint()
