#!/usr/bin/env python3
"""
Test script to identify schema import issues.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def test_individual_schemas():
    """Test each schema file individually to find the problematic one."""
    
    schemas = [
        ("User Schema", "app.schemas.user", ["UserCreate", "UserResponse"]),
        ("Vessel Schema", "app.schemas.vessel", ["VesselCreate", "VesselResponse"]),
        ("Calculation Schema", "app.schemas.calculation", ["CalculationCreate", "CalculationResponse"]),
        ("Organization Schema", "app.schemas.organization", ["OrganizationCreate", "Organization"]),
        ("Project Schema", "app.schemas.project", ["ProjectCreate", "Project"]),
        ("Material Schema", "app.schemas.material", ["MaterialCreate", "Material"]),
    ]
    
    for schema_name, module_name, classes in schemas:
        try:
            print(f"Testing {schema_name}...")
            module = __import__(module_name, fromlist=classes)
            
            for class_name in classes:
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    print(f"  ✅ {class_name} imported successfully")
                else:
                    print(f"  ⚠️ {class_name} not found in {module_name}")
            
        except Exception as e:
            print(f"  ❌ {schema_name} failed: {e}")
            print(f"     Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_individual_schemas()
