"""
Minimal test to debug the organization creation issue.
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)

from app.db.base import SessionLocal
from app.db.models.organization import Organization, SubscriptionType

def test_organization_creation():
    """Test creating an organization directly."""
    db = SessionLocal()
    
    try:
        print("Creating test organization...")
        
        # Create a simple organization
        org = Organization(
            name="Test Organization",
            description="Test organization for debugging",
            subscription_type=SubscriptionType.TRIAL,
            is_active=True
        )
        
        print(f"Organization object created: {org}")
        print(f"Subscription type: {org.subscription_type}")
        print(f"Subscription type value: {org.subscription_type.value}")
        
        db.add(org)
        print("Organization added to session")
        
        db.commit()
        print("Transaction committed successfully")
        
        db.refresh(org)
        print(f"Organization created with ID: {org.id}")
        
        return True
        
    except Exception as e:
        print(f"Error creating organization: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

def test_user_query():
    """Test querying existing users."""
    db = SessionLocal()
    
    try:
        from app.db.models.user import User
        
        print("Querying for existing users...")
        users = db.query(User).all()
        print(f"Found {len(users)} existing users")
        
        # Try the specific query that's failing
        user = db.query(User).filter(User.email == "test@email.com").first()
        if user:
            print(f"Found user with email test@email.com: {user.id}")
        else:
            print("No user found with email test@email.com")
            
        return True
        
    except Exception as e:
        print(f"Error querying users: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing database operations...")
    print("=" * 50)
    
    print("\n1. Testing user query...")
    test_user_query()
    
    print("\n2. Testing organization creation...")
    test_organization_creation()
