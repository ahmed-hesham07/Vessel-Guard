#!/usr/bin/env python3
"""
Simple test script to check if API endpoints are working after fixes.
"""

import requests
import json

def test_endpoint(url, description):
    """Test an API endpoint and print the result."""
    try:
        print(f"\n🧪 Testing {description}:")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS")
        elif response.status_code == 401:
            print("   🔐 Authentication required (expected)")
        elif response.status_code == 500:
            print("   ❌ INTERNAL SERVER ERROR")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            
        # Try to show first 200 chars of response
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                content = json.dumps(response.json(), indent=2)[:200]
                print(f"   Response: {content}...")
            else:
                content = response.text[:200]
                print(f"   Response: {content}...")
        except:
            print("   Response: <Could not parse>")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {e}")

def main():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("🚀 Testing Vessel Guard API after bug fixes")
    print("=" * 60)
    
    # Test endpoints that were failing
    endpoints = [
        ("/api/v1/calculations/", "Calculations endpoint"),
        ("/api/v1/reports/", "Reports endpoint"),
        ("/api/v1/projects/", "Projects endpoint"),
        ("/api/v1/vessels/", "Vessels endpoint"),
        ("/api/v1/inspections/", "Inspections endpoint"),
    ]
    
    for endpoint, description in endpoints:
        test_endpoint(f"{base_url}{endpoint}", description)
    
    print("\n" + "=" * 60)
    print("Test completed! Check logs above for any remaining issues.")
    print("=" * 60)

if __name__ == "__main__":
    main()
