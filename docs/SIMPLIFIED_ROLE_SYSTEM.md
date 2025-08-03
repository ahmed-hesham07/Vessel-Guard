# Simplified Role-Based Access Control System

## Overview

The Vessel Guard platform has been simplified to use only two user roles: **Engineer** and **Consultant**. This streamlined approach provides clear access levels while maintaining security and functionality.

## User Roles

### 1. Engineer
**Full access to all core features**

**Permissions:**
- ✅ Create, read, update, and delete projects
- ✅ Create, read, update, and delete vessels
- ✅ Perform all types of engineering calculations
- ✅ Create, update, and delete calculations
- ✅ Create, read, update, and delete inspections
- ✅ Generate comprehensive technical reports
- ✅ Manage materials and specifications
- ✅ Delete resources (projects, vessels, calculations, inspections)
- ✅ Full access to all data within their organization

**Use Case:** Primary users who need complete access to all platform features for engineering work, inspections, and report generation.

### 2. Consultant
**Read access to most features with limited write access**

**Permissions:**
- ✅ Create, read, and update projects (no deletion)
- ✅ Create, read, and update vessels (no deletion)
- ✅ Perform engineering calculations
- ✅ Create and update calculations (no deletion)
- ✅ Create, read, and update inspections (no deletion)
- ✅ Generate comprehensive technical reports
- ✅ Read and update materials (no deletion)
- ✅ Limited access to organization data

**Use Case:** External consultants or junior engineers who need to perform work but shouldn't have deletion privileges.

## Key Features

### Automatic Report Generation
Both Engineers and Consultants can:
- Complete inspections to automatically generate technical professional formal reports
- Receive email notifications when reports are ready
- Download and view generated reports
- Access comprehensive report features

### Calculation Engine
Both roles can:
- Perform engineering calculations
- Execute complex mathematical operations
- Generate calculation reports
- Access calculation history

### Inspection Management
Both roles can:
- Create and schedule inspections
- Update inspection status
- Mark inspections as completed
- Generate automatic reports upon completion

## Role Hierarchy

```
CONSULTANT (Level 1)
    ↓
ENGINEER (Level 2)
```

- Engineers have all Consultant permissions plus additional deletion and management capabilities
- Consultants have read/write access but cannot delete resources
- Both roles can perform core engineering functions

## Security Features

### Organization Isolation
- Users can only access data from their own organization
- Cross-organization access is prevented
- Data is automatically filtered by organization

### Permission Validation
- All API endpoints validate user permissions
- Role-based access control is enforced at the API level
- Invalid access attempts are logged and blocked

### Session Management
- Secure JWT token authentication
- Session tracking and management
- Automatic session expiration

## Implementation Details

### Backend Changes
- Updated `UserRole` enum to only include `ENGINEER` and `CONSULTANT`
- Simplified RBAC permissions mapping
- Updated API endpoint role requirements
- Streamlined user management functions

### Frontend Changes
- Updated user interface to reflect simplified roles
- Modified role selection components
- Updated permission checks in UI components

### Database
- Existing users with old roles will need to be migrated
- New users default to `ENGINEER` role
- Role validation ensures only valid roles are assigned

## Migration Guide

### For Existing Users
1. **Admin/Manager users** → Convert to **Engineer**
2. **Inspector users** → Convert to **Engineer** or **Consultant** based on needs
3. **Viewer users** → Convert to **Consultant**

### For New Users
- Default role: **Engineer**
- Can be changed to **Consultant** if limited access is needed

## Benefits

### Simplified Management
- Only two roles to manage
- Clear permission boundaries
- Reduced complexity in user administration

### Enhanced Security
- Reduced attack surface
- Clearer access control
- Easier to audit and monitor

### Improved User Experience
- Clear role expectations
- Consistent access levels
- Simplified onboarding process

## Usage Examples

### Creating a New User
```python
# Default role is ENGINEER
new_user = User(
    email="engineer@company.com",
    role=UserRole.ENGINEER,
    organization_id=1
)

# For consultant access
consultant_user = User(
    email="consultant@company.com",
    role=UserRole.CONSULTANT,
    organization_id=1
)
```

### Checking Permissions
```python
# Check if user can delete resources
if user.role == UserRole.ENGINEER:
    # Allow deletion
    pass
else:
    # Restrict deletion
    pass
```

### API Endpoint Protection
```python
@router.post("/projects")
def create_project(
    current_user: User = Depends(require_role(["engineer", "consultant"]))
):
    # Both engineers and consultants can create projects
    pass

@router.delete("/projects/{id}")
def delete_project(
    current_user: User = Depends(require_role(["engineer"]))
):
    # Only engineers can delete projects
    pass
```

## Future Enhancements

While the current system is simplified, future enhancements could include:

1. **Custom Permissions**: Fine-grained permission system for specific features
2. **Role Templates**: Predefined permission sets for different job functions
3. **Temporary Access**: Time-limited elevated permissions for specific tasks
4. **Audit Logging**: Enhanced tracking of permission changes and access patterns

## Support

For questions about the simplified role system or assistance with migration, please contact the development team. 