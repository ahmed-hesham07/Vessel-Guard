# Vessel Guard API Documentation

## 📚 **Comprehensive API Reference Guide**

Welcome to the Vessel Guard API - a powerful, enterprise-grade REST API for engineering calculations, vessel management, and compliance tracking. This documentation provides everything you need to integrate with our platform efficiently.

---

## 🚀 **Quick Start**

### **Base URL**
```
Production: https://api.vessel-guard.com/api/v1
Staging: https://staging-api.vessel-guard.com/api/v1
```

### **Authentication**
All API requests require authentication using JWT tokens:

```http
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

### **Your First API Call**
```bash
# Get your user profile
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.vessel-guard.com/api/v1/users/profile

# List your projects
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.vessel-guard.com/api/v1/projects
```

---

## 🔐 **Authentication & Authorization**

### **Login and Get Token**
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=your-email@company.com&password=your-password
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": 123,
    "email": "your-email@company.com",
    "name": "John Engineer",
    "role": "engineer",
    "organization_id": 456
  }
}
```

### **Refresh Token**
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

### **Role-Based Access Control**
- **Engineer**: Full access to calculations, projects, vessels, reports
- **Consultant**: Read-only access with limited modification rights

---

## 📖 **Core Resources**

### **Projects** - `/projects`

Projects are the top-level containers for your engineering work.

#### **List Projects**
```http
GET /projects?page=1&per_page=50&search=pressure&status=active
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (1-1000, default: 50)
- `search` (string): Search in project names and descriptions
- `status` (string): Filter by status (active, completed, archived)
- `sort_by` (string): Sort field (created_at, name, status)
- `sort_order` (string): Sort order (asc, desc)

**Response:**
```json
{
  "items": [
    {
      "id": 123,
      "name": "Refinery Pressure Vessel Analysis",
      "description": "ASME VIII compliance analysis for new pressure vessels",
      "project_code": "REF-2024-001",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:22:00Z",
      "organization_id": 456,
      "vessel_count": 15,
      "calculation_count": 45
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 127,
    "pages": 3,
    "has_next": true,
    "has_prev": false,
    "links": {
      "next": "/projects?page=2",
      "first": "/projects?page=1",
      "last": "/projects?page=3"
    }
  }
}
```

#### **Create Project**
```http
POST /projects
Content-Type: application/json

{
  "name": "New Refinery Project",
  "description": "Pressure vessel analysis for new refinery expansion",
  "project_code": "REF-2024-002",
  "start_date": "2024-02-01",
  "end_date": "2024-06-30",
  "tags": ["ASME", "pressure-vessel", "refinery"]
}
```

**Response:**
```json
{
  "id": 124,
  "name": "New Refinery Project",
  "project_code": "REF-2024-002",
  "status": "active",
  "created_at": "2024-01-21T09:15:00Z",
  "organization_id": 456
}
```

### **Vessels** - `/vessels`

Vessels represent the physical equipment being analyzed.

#### **List Vessels**
```http
GET /vessels?project_id=123&vessel_type=pressure_vessel
```

#### **Create Vessel**
```http
POST /vessels
Content-Type: application/json

{
  "project_id": 123,
  "tag_number": "V-101",
  "name": "Main Reactor Vessel",
  "vessel_type": "pressure_vessel",
  "design_pressure": 150.0,
  "design_temperature": 400.0,
  "material": "SA-516 Grade 70",
  "diameter": 48.0,
  "thickness": 1.25,
  "specifications": {
    "code": "ASME VIII Div 1",
    "corrosion_allowance": 0.125,
    "joint_efficiency": 1.0
  }
}
```

### **Calculations** - `/calculations`

Engineering calculations for vessel analysis and compliance.

#### **Create Calculation**
```http
POST /calculations
Content-Type: application/json

{
  "vessel_id": 789,
  "calculation_type": "pressure_vessel_asme_viii_div1",
  "input_parameters": {
    "design_pressure": 150.0,
    "design_temperature": 400.0,
    "diameter": 48.0,
    "thickness": 1.25,
    "material": "SA-516 Grade 70",
    "corrosion_allowance": 0.125,
    "joint_efficiency": 1.0
  },
  "calculation_options": {
    "include_fatigue_analysis": true,
    "safety_factor": 4.0,
    "units": "imperial"
  }
}
```

**Response:**
```json
{
  "id": 567,
  "vessel_id": 789,
  "calculation_type": "pressure_vessel_asme_viii_div1",
  "status": "completed",
  "results": {
    "allowable_stress": 20000.0,
    "required_thickness": 1.18,
    "actual_thickness": 1.25,
    "safety_margin": 5.9,
    "compliance_status": "compliant",
    "applicable_codes": ["ASME VIII Div 1", "ASME B31.3"]
  },
  "created_at": "2024-01-21T10:30:00Z",
  "calculated_by": {
    "id": 123,
    "name": "John Engineer"
  }
}
```

### **Reports** - `/reports`

Generate comprehensive reports for compliance and documentation.

#### **Generate Report**
```http
POST /reports
Content-Type: application/json

{
  "title": "Pressure Vessel Compliance Report",
  "report_type": "compliance",
  "project_id": 123,
  "vessel_ids": [789, 790, 791],
  "calculation_ids": [567, 568, 569],
  "include_sections": [
    "executive_summary",
    "design_parameters",
    "calculations",
    "compliance_analysis",
    "recommendations"
  ],
  "format": "pdf",
  "template": "asme_compliance_standard"
}
```

---

## ⚡ **Advanced Features**

### **Bulk Operations**

Efficiently process multiple items in single requests.

#### **Bulk Create Projects**
```http
POST /bulk/projects/create
Content-Type: application/json

{
  "projects": [
    {
      "name": "Project 1",
      "project_code": "PROJ-001",
      "description": "First project"
    },
    {
      "name": "Project 2", 
      "project_code": "PROJ-002",
      "description": "Second project"
    }
  ],
  "skip_duplicates": true,
  "continue_on_error": true
}
```

**Response:**
```json
{
  "success_count": 2,
  "error_count": 0,
  "total_count": 2,
  "success_ids": [125, 126],
  "errors": [],
  "warnings": []
}
```

### **Field Selection**

Optimize responses by selecting only needed fields:

```http
GET /projects?fields=id,name,status&exclude=description,internal_notes
```

### **Advanced Search**

Powerful search with relevance scoring:

```http
GET /projects/search/advanced?q=pressure&fuzzy_search=true&highlight_matches=true
```

### **Conditional Data Loading**

Load related data only when needed:

```http
GET /projects/123?include_vessels=true&include_calculations=true&include_stats=true
```

---

## 📊 **Response Formats**

### **Standard Response Structure**
```json
{
  "data": { /* your requested data */ },
  "meta": {
    "timestamp": "2024-01-21T10:30:00Z",
    "api_version": "1.0",
    "request_id": "req_123456789"
  }
}
```

### **Paginated Response**
```json
{
  "items": [ /* array of items */ ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 127,
    "pages": 3,
    "has_next": true,
    "has_prev": false,
    "links": {
      "next": "/endpoint?page=2",
      "prev": null,
      "first": "/endpoint?page=1",
      "last": "/endpoint?page=3"
    }
  },
  "meta": {
    "filters_applied": {
      "search": "pressure",
      "status": "active"
    }
  }
}
```

### **Error Response**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "details": {
      "field_errors": {
        "design_pressure": [
          "Pressure must be at least 0 psi, got -10 psi"
        ]
      }
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-21T10:30:00Z"
  }
}
```

---

## 🔧 **Engineering Calculations**

### **Supported Calculation Types**

#### **Pressure Vessels**
- `pressure_vessel_asme_viii_div1`: ASME VIII Division 1 analysis
- `pressure_vessel_asme_viii_div2`: ASME VIII Division 2 analysis
- `pressure_vessel_en_13445`: European EN 13445 standard
- `fitness_for_service_api579`: API 579/ASME FFS-1 analysis

#### **Piping Systems**
- `piping_asme_b31_3`: Process piping per ASME B31.3
- `piping_asme_b31_1`: Power piping per ASME B31.1
- `piping_stress_analysis`: Comprehensive stress analysis

#### **Heat Exchangers**
- `heat_exchanger_tema`: TEMA standard analysis
- `heat_exchanger_asme_viii`: Pressure vessel rules for heat exchangers

### **Input Parameters by Type**

#### **Pressure Vessel Parameters**
```json
{
  "design_pressure": 150.0,          // psi
  "design_temperature": 400.0,       // °F
  "diameter": 48.0,                  // inches
  "thickness": 1.25,                 // inches
  "material": "SA-516 Grade 70",     // Material specification
  "corrosion_allowance": 0.125,      // inches
  "joint_efficiency": 1.0,           // 0.0 - 1.0
  "head_type": "ellipsoidal",        // ellipsoidal, hemispherical, torispherical
  "weld_type": "full_penetration"    // full_penetration, partial_penetration
}
```

#### **Piping Parameters**
```json
{
  "nominal_pipe_size": "6",          // NPS
  "schedule": "40",                  // Pipe schedule
  "material": "A106 Grade B",        // Material specification
  "design_pressure": 150.0,          // psi
  "design_temperature": 400.0,       // °F
  "fluid_density": 62.4,             // lb/ft³
  "flow_rate": 1000.0,               // gpm
  "pipe_length": 100.0,              // feet
  "fittings": [                      // Array of fittings
    {"type": "elbow_90", "quantity": 4},
    {"type": "gate_valve", "quantity": 1}
  ]
}
```

### **Calculation Results Structure**
```json
{
  "compliance_status": "compliant",   // compliant, non_compliant, warning
  "safety_factor": 3.2,              // Calculated safety factor
  "allowable_stress": 20000.0,       // psi
  "required_thickness": 1.18,        // inches
  "actual_thickness": 1.25,          // inches
  "safety_margin": 5.9,              // percentage
  "applicable_codes": [               // Relevant standards
    "ASME VIII Div 1",
    "ASME B31.3"
  ],
  "warnings": [                      // Any warnings or notes
    "Design pressure is near material limit"
  ],
  "detailed_results": {              // Detailed calculation steps
    "hoop_stress": 12000.0,
    "longitudinal_stress": 6000.0,
    "combined_stress": 13416.4
  }
}
```

---

## 📈 **Performance Optimization**

### **Response Time Headers**
Monitor API performance with automatic headers:
```http
X-Response-Time: 0.125s
X-Performance-Score: 85/100
X-Cache-Status: HIT
```

### **Optimization Hints**
Get automatic suggestions for better performance:
```http
X-Optimization-Hint: use pagination; enable compression
```

### **Field Selection**
Reduce response size by selecting only needed fields:
```http
GET /projects?fields=id,name,status
# Returns only id, name, and status fields

GET /projects?exclude=internal_notes,debug_info  
# Returns all fields except excluded ones
```

### **Compression**
All responses are automatically compressed with gzip when supported.

### **Caching**
- Static data: 1 hour cache
- Dynamic data: 5 minutes cache with revalidation
- User-specific data: No cache

---

## 🚨 **Error Handling**

### **HTTP Status Codes**
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### **Error Codes**
| Code | Description | Action |
|------|-------------|---------|
| `AUTH_001` | Authentication failed | Check credentials |
| `AUTH_002` | Invalid credentials | Verify email/password |
| `AUTH_003` | Token expired | Refresh token |
| `VAL_001` | Validation error | Check input parameters |
| `RES_001` | Resource not found | Verify resource ID |
| `BIZ_001` | Business rule violation | Check business logic |
| `SYS_003` | Rate limit exceeded | Reduce request frequency |

### **Validation Errors**
Detailed field-level validation errors:
```json
{
  "error": {
    "code": "VAL_001",
    "message": "Validation failed",
    "field_errors": {
      "design_pressure": [
        "Pressure must be at least 0 psi, got -10 psi",
        "Value is outside typical range for this application"
      ],
      "material": [
        "Material specification not found in database"
      ]
    },
    "suggestions": [
      "Check engineering unit conversions",
      "Verify material specifications against ASME standards"
    ]
  }
}
```

---

## ⚡ **Rate Limiting**

### **Rate Limits**
- **Standard endpoints**: 1000 requests per hour
- **Bulk operations**: 100 requests per hour  
- **Calculation endpoints**: 500 requests per hour
- **Search endpoints**: 200 requests per hour

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642771200
```

### **Rate Limit Exceeded**
```json
{
  "error": {
    "code": "SYS_003", 
    "message": "Rate limit exceeded",
    "details": {
      "limit": 1000,
      "window": "1 hour",
      "reset_at": "2024-01-21T11:00:00Z"
    }
  }
}
```

---

## 🔍 **Testing Your Integration**

### **Postman Collection**
Download our complete Postman collection:
```
https://api.vessel-guard.com/postman/vessel-guard-api.json
```

### **Sample Workflow**
1. **Authenticate**: Get access token
2. **Create Project**: Set up your engineering project
3. **Add Vessels**: Define equipment to analyze
4. **Run Calculations**: Perform engineering analysis
5. **Generate Report**: Create compliance documentation

### **Test Data**
Use our sandbox environment with pre-populated test data:
```
Base URL: https://sandbox-api.vessel-guard.com/api/v1
Test Account: test@vessel-guard.com / TestPassword123
```

---

## 📱 **SDKs and Libraries**

### **Official SDKs**
- **Python**: `pip install vessel-guard-python`
- **JavaScript/Node.js**: `npm install vessel-guard-js`
- **C#/.NET**: `Install-Package VesselGuard.SDK`

### **Python Example**
```python
from vessel_guard import VesselGuardClient

client = VesselGuardClient(
    api_key="your_api_key",
    base_url="https://api.vessel-guard.com"
)

# Create a project
project = client.projects.create({
    "name": "My Engineering Project",
    "description": "ASME compliance analysis"
})

# Add a vessel
vessel = client.vessels.create({
    "project_id": project.id,
    "tag_number": "V-101",
    "vessel_type": "pressure_vessel",
    "design_pressure": 150.0,
    "design_temperature": 400.0
})

# Run calculation
calculation = client.calculations.create({
    "vessel_id": vessel.id,
    "calculation_type": "pressure_vessel_asme_viii_div1",
    "input_parameters": {
        "design_pressure": 150.0,
        "design_temperature": 400.0,
        "diameter": 48.0,
        "thickness": 1.25
    }
})

print(f"Calculation result: {calculation.results.compliance_status}")
```

---

## 🛠️ **Webhook Support**

### **Event Types**
- `calculation.completed`: Calculation finished
- `calculation.failed`: Calculation error
- `report.generated`: Report ready for download
- `project.status_changed`: Project status update

### **Webhook Configuration**
```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhook/vessel-guard",
  "events": ["calculation.completed", "report.generated"],
  "secret": "your_webhook_secret"
}
```

### **Webhook Payload**
```json
{
  "event": "calculation.completed",
  "data": {
    "calculation_id": 567,
    "vessel_id": 789,
    "project_id": 123,
    "status": "completed",
    "compliance_status": "compliant"
  },
  "timestamp": "2024-01-21T10:30:00Z"
}
```

---

## 📋 **Best Practices**

### **Authentication**
- Store tokens securely
- Implement token refresh logic
- Use HTTPS for all requests
- Rotate API keys regularly

### **Performance**
- Use field selection for large responses
- Implement pagination for list endpoints
- Cache responses when appropriate
- Use bulk operations for multiple items

### **Error Handling**
- Implement exponential backoff for retries
- Handle rate limiting gracefully
- Log API errors for debugging
- Validate input before sending requests

### **Data Validation**
- Validate engineering parameters against standards
- Check unit consistency
- Verify material specifications
- Review calculation results for reasonableness

---

## 📞 **Support and Resources**

### **Documentation Links**
- [User Guide](USER_GUIDE.md) - Complete user documentation
- [Developer Guide](DEVELOPER_GUIDE.md) - Setup and development
- [Architecture Guide](ARCHITECTURE.md) - System design and security

### **Community and Support**
- **API Status**: [status.vessel-guard.com](https://status.vessel-guard.com)
- **Support Portal**: [support.vessel-guard.com](https://support.vessel-guard.com)
- **Developer Forum**: [developers.vessel-guard.com](https://developers.vessel-guard.com)
- **GitHub Issues**: [github.com/vessel-guard/api-issues](https://github.com/vessel-guard/api-issues)

### **Contact Information**
- **Technical Support**: api-support@vessel-guard.com
- **Sales Inquiries**: sales@vessel-guard.com
- **Partnership**: partnerships@vessel-guard.com

---

## 🔄 **API Versioning**

### **Current Version**: v1
- **Stability**: Production ready
- **Support**: Full support and maintenance
- **Breaking Changes**: None planned

### **Version Headers**
```http
Accept: application/json; version=1
API-Version: 1.0
```

### **Deprecation Policy**
- 90-day notice for breaking changes
- 180-day support for deprecated endpoints
- Clear migration documentation provided

---

*This documentation is continuously updated. Last updated: December 2024*