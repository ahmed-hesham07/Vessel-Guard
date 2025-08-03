"""
Debug script to test the registration endpoint with detailed error reporting.
"""

import requests
import json

def test_registration_debug():
    """Test user registration endpoint with detailed debugging."""
    url = "http://localhost:8000/api/v1/auth/register"
    
    # Test data - using a different email to avoid conflicts
    user_data = {
        "email": "test@email.com",
        "password": "StrongPassword456!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "5551234567", 
        "job_title": "Test Engineer",
        "department": "Testing",
        "organization_name": "Test Organization"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to: {url}")
    print(f"Request data: {json.dumps(user_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=user_data, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            result = response.json()
            print(f"User ID: {result.get('user', {}).get('id')}")
            print(f"User Email: {result.get('user', {}).get('email')}")
            return True
        else:
            print("❌ Registration failed!")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server!")
        print("Make sure the backend is running on http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health():
    """Test health endpoint."""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend is healthy!")
            return True
        else:
            print("❌ Backend health check failed!")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("Debugging Vessel Guard Registration API...")
    print("=" * 60)
    
    # Test health first
    print("1. Testing health endpoint...")
    if not test_health():
        print("⚠️  Backend may not be running, but trying registration anyway...")
    
    print("\n2. Testing registration endpoint...")
    test_registration_debug()
