"""
Test script to verify the registration endpoint is working.
"""

import requests
import json

def test_registration():
    """Test user registration endpoint."""
    url = "http://localhost:8000/api/v1/auth/register"
    
    # Test data
    user_data = {
        "email": "engineer@company.com",
        "password": "StrongPassword456!",
        "first_name": "John",
        "last_name": "Smith",
        "phone": "5551234567", 
        "job_title": "Pressure Vessel Engineer",
        "department": "Mechanical Engineering",
        "organization_name": "Industrial Solutions Inc"
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.post(url, json=user_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health():
    """Test health endpoint."""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url)
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Vessel Guard API...")
    print("=" * 50)
    
    # Test health first
    print("1. Testing health endpoint...")
    if test_health():
        print("✅ Backend is running!")
    else:
        print("❌ Backend is not running!")
        exit(1)
    
    print("\n2. Testing registration endpoint...")
    test_registration()
