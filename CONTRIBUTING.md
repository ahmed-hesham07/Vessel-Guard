# Contributing to Vessel Guard

Thank you for your interest in contributing to Vessel Guard! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- PostgreSQL (for production) or SQLite (for development)
- Redis (optional, for caching)
- Git

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/Vessel-Guard.git
   cd Vessel-Guard
   ```

2. **Install Dependencies**
   ```bash
   # Install root dependencies
   npm install
   
   # Install frontend dependencies
   cd apps/frontend
   npm install
   
   # Install backend dependencies
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Copy environment files
   cp .env.example .env
   cp apps/frontend/.env.example apps/frontend/.env.local
   cp apps/backend/.env.example apps/backend/.env
   ```

4. **Database Setup**
   ```bash
   # Run database migrations
   cd apps/backend
   python setup_dev.py
   ```

5. **Start Development Servers**
   ```bash
   # Start both frontend and backend
   npm run dev
   
   # Or start individually
   npm run dev:frontend  # Frontend on :3000
   npm run dev:backend   # Backend on :8000
   ```

## Contribution Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Found a bug? Please create an issue with detailed information
- **Feature Requests**: Have an idea? Open an issue to discuss it
- **Code Contributions**: Fix bugs, implement features, improve documentation
- **Documentation**: Improve our docs, add examples, write tutorials
- **Testing**: Add tests, improve test coverage

### Before You Start

1. **Check Existing Issues**: Look for existing issues or discussions
2. **Create an Issue**: For new features or bugs, create an issue first
3. **Discuss**: Comment on the issue to discuss your approach
4. **Get Assigned**: Wait for maintainers to assign the issue to you

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write clean, well-commented code
- Follow our coding standards
- Add or update tests as needed
- Update documentation if necessary

### 3. Test Your Changes

```bash
# Run all tests
npm run test

# Run frontend tests
cd apps/frontend
npm run test
npm run test:e2e

# Run backend tests
cd apps/backend
python -m pytest tests/ -v
```

### 4. Commit Your Changes

We use conventional commits. Format your commit messages as:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```bash
git commit -m "feat(auth): add password reset functionality"
git commit -m "fix(calculations): correct ASME B31.3 stress calculation"
git commit -m "docs(api): update endpoint documentation"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request with:
- Clear title and description
- Link to related issues
- Screenshots for UI changes
- Test coverage information

### 6. Code Review

- Address review feedback promptly
- Keep your branch up to date with main
- Be open to suggestions and discussions

## Coding Standards

### Frontend (TypeScript/React)

- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks
- Implement proper error boundaries
- Use Tailwind CSS for styling
- Follow the established component structure

```typescript
// Good
interface ButtonProps {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  onClick?: () => void
  children: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  children,
}) => {
  return (
    <button
      className={cn(
        'rounded-md font-medium transition-colors',
        variants[variant],
        sizes[size]
      )}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
```

### Backend (Python/FastAPI)

- Follow PEP 8 style guide
- Use type hints consistently
- Write docstrings for all functions/classes
- Use Pydantic for data validation
- Follow the established API structure

```python
# Good
from typing import List, Optional
from pydantic import BaseModel, Field

class VesselCreateRequest(BaseModel):
    """Request model for creating a new vessel."""
    
    tag_number: str = Field(..., description="Unique vessel tag number")
    description: str = Field(..., description="Vessel description")
    vessel_type: str = Field(..., description="Type of vessel")
    design_pressure: float = Field(gt=0, description="Design pressure in PSI")
    design_temperature: float = Field(description="Design temperature in °F")

async def create_vessel(
    vessel_data: VesselCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> VesselResponse:
    """Create a new vessel in the system."""
    vessel = Vessel(**vessel_data.dict(), owner_id=current_user.id)
    db.add(vessel)
    db.commit()
    db.refresh(vessel)
    return VesselResponse.from_orm(vessel)
```

### File Organization

```
apps/
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js app router pages
│   │   ├── components/    # Reusable components
│   │   │   ├── ui/        # Basic UI components
│   │   │   └── layout/    # Layout components
│   │   ├── contexts/      # React contexts
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── tests/             # Test files
│
└── backend/
    ├── app/
    │   ├── api/           # API routes
    │   ├── core/          # Core configuration
    │   ├── crud/          # Database operations
    │   ├── db/            # Database models
    │   ├── schemas/       # Pydantic schemas
    │   └── services/      # Business logic
    └── tests/             # Test files
```

## Testing

### Frontend Testing

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows

```bash
# Run unit tests
npm run test

# Run E2E tests
npm run test:e2e

# Run tests with coverage
npm run test:coverage
```

### Backend Testing

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints
- **Database Tests**: Test data operations

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=app --cov-report=html
```

### Test Guidelines

- Write tests for all new features
- Maintain minimum 80% test coverage
- Use descriptive test names
- Test both happy path and error cases
- Mock external dependencies

## Documentation

### Code Documentation

- Add JSDoc comments for TypeScript functions
- Add docstrings for Python functions/classes
- Document complex business logic
- Keep README files updated

### API Documentation

- Use OpenAPI/Swagger for API documentation
- Document all endpoints, parameters, and responses
- Provide examples for complex requests

### User Documentation

- Update user guides for new features
- Create tutorials for complex workflows
- Maintain troubleshooting guides

## Release Process

1. **Version Bump**: Update version numbers
2. **Changelog**: Update CHANGELOG.md
3. **Testing**: Run full test suite
4. **Documentation**: Update documentation
5. **Release**: Create release tag and notes

## Getting Help

- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our Discord server for real-time chat
- **Email**: Contact maintainers directly for security issues

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors section

Thank you for contributing to Vessel Guard! 🚀
