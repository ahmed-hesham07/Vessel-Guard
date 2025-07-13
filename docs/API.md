# API Documentation

## Vessel Guard Engineering API

The Vessel Guard API provides comprehensive engineering calculations and compliance verification for pressure vessels, piping systems, and related equipment according to industry standards including ASME B31.3, API 579, and ASME VIII.

### Base URL

- **Production**: `https://api.vesselguard.com`
- **Staging**: `https://staging-api.vesselguard.com`
- **Development**: `http://localhost:8000`

### Authentication

The API uses JWT (JSON Web Token) based authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

#### Obtaining a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "role": "engineer"
  }
}
```

### API Versioning

The API uses URL-based versioning. Current version is `v1`.

All endpoints are prefixed with `/api/v1/`

### Rate Limiting

API requests are rate-limited to ensure fair usage:

- **Per IP**: 1000 requests/hour, 100 requests/minute
- **Per User**: 10,000 requests/hour
- **Global**: 50,000 requests/hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Reset time (Unix timestamp)

### Error Handling

The API uses conventional HTTP status codes and returns JSON error responses:

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field": "Specific field error information"
  }
}
```

#### Common Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Pagination

List endpoints support pagination using query parameters:

- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Sort field (default: created_at)
- `order`: Sort order (asc/desc, default: desc)

**Example:**
```http
GET /api/v1/projects?page=2&limit=50&sort=name&order=asc
```

**Response includes pagination metadata:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 150,
    "pages": 3,
    "has_next": true,
    "has_prev": true
  }
}
```

## Endpoints

### Health Checks

#### Basic Health Check
```http
GET /api/v1/health
```

Returns basic service status.

#### Detailed Health Check
```http
GET /api/v1/health/detailed
```

Returns detailed health including database and cache status.

#### System Health Check
```http
GET /api/v1/health/system
```

Returns system resource usage (CPU, memory, disk).

#### Readiness Check
```http
GET /api/v1/health/readiness
```

Kubernetes readiness probe endpoint.

#### Liveness Check
```http
GET /api/v1/health/liveness
```

Kubernetes liveness probe endpoint.

### Authentication

#### Login
```http
POST /api/v1/auth/login
```

Authenticate user and receive JWT token.

#### Logout
```http
POST /api/v1/auth/logout
```

Invalidate current JWT token.

#### Token Refresh
```http
POST /api/v1/auth/refresh
```

Refresh JWT token before expiration.

#### Register
```http
POST /api/v1/auth/register
```

Register new user account.

### User Management

#### Get Current User
```http
GET /api/v1/users/me
```

Get current authenticated user information.

#### Update Profile
```http
PUT /api/v1/users/me
```

Update current user profile.

#### Change Password
```http
POST /api/v1/users/me/password
```

Change current user password.

### Projects

#### List Projects
```http
GET /api/v1/projects
```

Get paginated list of projects for the current user.

#### Create Project
```http
POST /api/v1/projects
```

Create a new engineering project.

**Request Body:**
```json
{
  "name": "Refinery Piping System",
  "description": "ASME B31.3 compliance verification",
  "client_name": "ABC Refinery",
  "project_number": "PRJ-2024-001",
  "standards": ["ASME_B31_3", "API_579"],
  "status": "active"
}
```

#### Get Project
```http
GET /api/v1/projects/{project_id}
```

Get detailed project information.

#### Update Project
```http
PUT /api/v1/projects/{project_id}
```

Update project information.

#### Delete Project
```http
DELETE /api/v1/projects/{project_id}
```

Delete a project (soft delete).

### Vessels

#### List Vessels
```http
GET /api/v1/vessels
```

Get paginated list of vessels.

#### Create Vessel
```http
POST /api/v1/vessels
```

Create a new pressure vessel.

**Request Body:**
```json
{
  "name": "Main Reactor",
  "tag_number": "V-101",
  "project_id": "project_uuid",
  "vessel_type": "pressure_vessel",
  "design_pressure": 150.0,
  "design_temperature": 300.0,
  "material_specification": "SA-516 Grade 70",
  "diameter": 2.5,
  "length": 6.0,
  "wall_thickness": 0.5,
  "corrosion_allowance": 0.125,
  "design_code": "ASME_VIII_DIV_1"
}
```

#### Get Vessel
```http
GET /api/v1/vessels/{vessel_id}
```

Get detailed vessel information.

#### Update Vessel
```http
PUT /api/v1/vessels/{vessel_id}
```

Update vessel specifications.

### Calculations

#### List Calculations
```http
GET /api/v1/calculations
```

Get paginated list of engineering calculations.

#### Perform ASME B31.3 Calculation
```http
POST /api/v1/calculations/asme-b31-3
```

Perform ASME B31.3 piping stress calculation.

**Request Body:**
```json
{
  "project_id": "project_uuid",
  "calculation_name": "Main Steam Line",
  "pipe_outside_diameter": 6.625,
  "wall_thickness": 0.280,
  "design_pressure": 600.0,
  "design_temperature": 750.0,
  "material_specification": "A106 Grade B",
  "joint_efficiency": 1.0,
  "corrosion_allowance": 0.0625,
  "temperature_derating_factor": 0.85
}
```

#### Perform API 579 Assessment
```http
POST /api/v1/calculations/api-579
```

Perform API 579 fitness-for-service assessment.

#### Perform ASME VIII Calculation
```http
POST /api/v1/calculations/asme-viii
```

Perform ASME VIII pressure vessel calculation.

#### Get Calculation Results
```http
GET /api/v1/calculations/{calculation_id}
```

Get detailed calculation results with engineering analysis.

### Engineering Standards

#### List Standards
```http
GET /api/v1/standards
```

Get available engineering standards and codes.

#### Get Standard Details
```http
GET /api/v1/standards/{standard_code}
```

Get detailed information about a specific standard.

### Materials

#### List Materials
```http
GET /api/v1/materials
```

Get material database with allowable stresses and properties.

#### Get Material Properties
```http
GET /api/v1/materials/{material_id}
```

Get detailed material properties and allowable stresses.

#### Search Materials
```http
GET /api/v1/materials/search?q={search_term}
```

Search materials by specification, grade, or properties.

### Reports

#### Generate Calculation Report
```http
POST /api/v1/reports/calculation/{calculation_id}
```

Generate comprehensive calculation report in PDF format.

#### List Reports
```http
GET /api/v1/reports
```

Get list of generated reports.

#### Download Report
```http
GET /api/v1/reports/{report_id}/download
```

Download report file.

### Inspections

#### List Inspections
```http
GET /api/v1/inspections
```

Get paginated list of vessel inspections.

#### Create Inspection Record
```http
POST /api/v1/inspections
```

Create new inspection record.

#### Get Inspection Details
```http
GET /api/v1/inspections/{inspection_id}
```

Get detailed inspection information.

### Organizations

#### Get Organization
```http
GET /api/v1/organizations/me
```

Get current user's organization information.

#### Update Organization
```http
PUT /api/v1/organizations/me
```

Update organization settings (admin only).

#### List Organization Users
```http
GET /api/v1/organizations/me/users
```

List users in the organization (admin only).

## Data Models

### Project
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "client_name": "string",
  "project_number": "string",
  "standards": ["ASME_B31_3", "API_579"],
  "status": "active|completed|archived",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by_id": "uuid"
}
```

### Vessel
```json
{
  "id": "uuid",
  "name": "string",
  "tag_number": "string",
  "project_id": "uuid",
  "vessel_type": "pressure_vessel|storage_tank|heat_exchanger",
  "design_pressure": 150.0,
  "design_temperature": 300.0,
  "material_specification": "string",
  "diameter": 2.5,
  "length": 6.0,
  "wall_thickness": 0.5,
  "corrosion_allowance": 0.125,
  "design_code": "ASME_VIII_DIV_1|ASME_VIII_DIV_2|API_650",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Calculation Result
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "calculation_type": "ASME_B31_3|API_579|ASME_VIII",
  "calculation_name": "string",
  "input_parameters": {},
  "results": {
    "allowable_pressure": 180.5,
    "calculated_thickness": 0.245,
    "safety_factor": 3.5,
    "compliance_status": "PASS|FAIL",
    "recommendations": ["string"]
  },
  "standard_references": ["string"],
  "calculation_date": "2024-01-01T00:00:00Z",
  "calculated_by_id": "uuid"
}
```

## Engineering Standards Support

### ASME B31.3 - Process Piping
- Allowable stress calculations
- Pressure design thickness
- Temperature derating factors
- Material specifications
- Joint efficiency factors
- Supplemental load requirements

### API 579 - Fitness for Service
- Local metal loss assessment
- General metal loss assessment
- Pitting damage assessment
- Blister and lamination assessment
- Crack-like flaw assessment

### ASME VIII - Pressure Vessels
- Division 1 design rules
- Division 2 alternative rules
- Allowable stress calculations
- Head and shell thickness calculations
- Reinforcement requirements

## SDK and Client Libraries

### Python SDK
```python
from vessel_guard import VesselGuardClient

client = VesselGuardClient(
    api_key="your_api_key",
    base_url="https://api.vesselguard.com"
)

# Perform calculation
result = client.calculations.asme_b31_3({
    "pipe_outside_diameter": 6.625,
    "wall_thickness": 0.280,
    "design_pressure": 600.0,
    # ... other parameters
})

print(f"Allowable pressure: {result.allowable_pressure} psi")
```

### JavaScript SDK
```javascript
import { VesselGuardClient } from '@vessel-guard/sdk';

const client = new VesselGuardClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.vesselguard.com'
});

// Perform calculation
const result = await client.calculations.asmeB313({
  pipeOutsideDiameter: 6.625,
  wallThickness: 0.280,
  designPressure: 600.0,
  // ... other parameters
});

console.log(`Allowable pressure: ${result.allowablePressure} psi`);
```

## Webhooks

Configure webhooks to receive real-time notifications:

### Supported Events
- `calculation.completed`
- `calculation.failed`
- `report.generated`
- `inspection.created`
- `project.updated`

### Webhook Configuration
```http
POST /api/v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/vessel-guard",
  "events": ["calculation.completed", "report.generated"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload
```json
{
  "event": "calculation.completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "calculation_id": "uuid",
    "project_id": "uuid",
    "status": "completed",
    "results": {}
  }
}
```

## Support and Resources

- **Documentation**: https://docs.vesselguard.com
- **API Status**: https://status.vesselguard.com
- **Support**: support@vesselguard.com
- **GitHub**: https://github.com/vessel-guard/api

### Rate Limit Increase Requests

For higher rate limits, contact support with:
- Use case description
- Expected request volume
- Business justification

### Custom Integration Support

Professional services available for:
- Custom calculation implementations
- Enterprise integrations
- On-premise deployments
- Compliance consulting
