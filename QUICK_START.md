# 🚀 Vessel Guard - Quick Start Guide

Welcome to **Vessel Guard**, the comprehensive engineering SaaS platform for pressure vessel integrity analysis and compliance management. This guide will get you up and running in minutes.

## 📋 Prerequisites

Before starting, ensure you have:

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.9+** - [Download here](https://python.org/)
- **Git** - [Download here](https://git-scm.com/)
- **Docker** (optional) - [Download here](https://docker.com/)

## ⚡ Quick Setup (5 minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/ahmed-hesham07/Vessel-Guard.git
cd Vessel-Guard
```

### 2. Run Setup Script
**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Linux/macOS:**
```bash
chmod +x setup.ps1
./setup.ps1
```

The setup script automatically:
- ✅ Installs all dependencies
- ✅ Sets up the database
- ✅ Configures environment files
- ✅ Prepares development tools

### 3. Start Development Servers
```bash
npm run dev
```

🎉 **That's it!** Your application is now running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 First Steps

### 1. Access the Application
Open your browser and navigate to http://localhost:3000

### 2. Create Your Account
1. Click "Sign Up" on the login page
2. Fill in your details
3. Verify your email (check logs for development)

### 3. Create Your First Project
1. Navigate to **Projects** → **New Project**
2. Enter project details:
   - **Name**: "My First Vessel"
   - **Description**: "Learning Vessel Guard"
   - **Type**: "Pressure Vessel"

### 4. Add a Vessel
1. Go to **Assets** → **New Asset**
2. Fill in vessel parameters:
   - **Tag Number**: "V-001"
   - **Design Pressure**: "150 psi"
   - **Design Temperature**: "300°F"
   - **Material**: "SA-516 Gr. 70"

### 5. Run Your First Calculation
1. Navigate to **Calculations** → **New Calculation**
2. Select calculation type: **"ASME VIII Div 1"**
3. Enter parameters and click **"Calculate"**
4. Review results and generate report

## 🛠 Development Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start full development environment |
| `npm run dev:frontend` | Frontend only (port 3000) |
| `npm run dev:backend` | Backend only (port 8000) |
| `npm run build` | Build for production |
| `npm test` | Run all tests |
| `npm run lint` | Check code quality |

## 🗂 Project Structure

```
Vessel-Guard/
├── apps/
│   ├── frontend/          # Next.js React application
│   │   ├── src/
│   │   │   ├── app/       # App router pages
│   │   │   ├── components/ # Reusable components
│   │   │   └── lib/       # Utilities and API
│   │   └── public/        # Static assets
│   └── backend/           # FastAPI Python application
│       ├── app/
│       │   ├── api/       # API endpoints
│       │   ├── models/    # Database models
│       │   ├── services/  # Business logic
│       │   └── utils/     # Engineering utilities
│       └── tests/         # Backend tests
├── docs/                  # Documentation
├── scripts/              # Utility scripts
└── package.json          # Root configuration
```

## 🔧 Configuration

### Environment Variables

**Backend** (`apps/backend/.env`):
```env
DATABASE_URL=sqlite:///./vessel_guard_dev.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
EMAIL_SERVER_HOST=localhost
EMAIL_SERVER_PORT=1025
```

**Frontend** (`apps/frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Vessel Guard
```

## 📚 Key Features

### ⚙️ Engineering Calculations
- **ASME VIII Div 1 & 2** - Pressure vessel design
- **ASME B31.3** - Process piping
- **API 579** - Fitness-for-service assessment
- **EN 13445** - European pressure equipment

### 📊 Project Management
- Multi-project organization
- Asset tracking and documentation
- Inspection scheduling and tracking
- Compliance reporting

### 📈 Analytics & Reporting
- Professional PDF reports
- Excel export capabilities
- Dashboard analytics
- Audit trails

### 👥 Team Collaboration
- Role-based access control
- Real-time collaboration
- Comment and review system
- Organization management

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Kill processes on ports
npx kill-port 3000 8000
```

**Database Issues:**
```bash
# Reset database
cd apps/backend
python -m alembic downgrade base
python -m alembic upgrade head
```

**Permission Errors (Windows):**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Python Virtual Environment:**
```bash
# Recreate if corrupted
cd apps/backend
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## 🚀 Production Deployment

### Using Docker
```bash
# Build and start
docker-compose up --build

# With specific environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Manual Deployment
```bash
# Build frontend
cd apps/frontend
npm run build

# Setup backend
cd ../backend
pip install -r requirements.txt
python -m alembic upgrade head

# Start production servers
npm run start
```

## 📖 Learning Resources

### Documentation
- 📘 [**User Guide**](./docs/USER_GUIDE.md) - Complete user documentation
- 🔧 [**API Documentation**](http://localhost:8000/docs) - Interactive API docs
- 🏗️ [**Architecture Guide**](./docs/ARCHITECTURE.md) - System architecture
- 🧪 [**Testing Guide**](./docs/TESTING.md) - Testing procedures

### Engineering Standards
- [ASME Boiler and Pressure Vessel Code](https://www.asme.org/codes-standards/find-codes-standards/bpvc-section-viii-division-1-pressure-vessels)
- [API 579 Fitness-for-Service](https://www.api.org/products-and-services/standards/api-579)
- [ASME B31.3 Process Piping](https://www.asme.org/codes-standards/find-codes-standards/b31-3-process-piping)

## 💬 Support & Community

### Getting Help
- 📧 **Email**: support@vessel-guard.com
- 💬 **Issues**: [GitHub Issues](https://github.com/ahmed-hesham07/Vessel-Guard/issues)
- 📖 **Documentation**: [Complete docs](./docs/)

### Contributing
- 🤝 [**Contributing Guide**](./CONTRIBUTING.md)
- 🐛 [**Bug Reports**](https://github.com/ahmed-hesham07/Vessel-Guard/issues/new?template=bug_report.md)
- ✨ [**Feature Requests**](https://github.com/ahmed-hesham07/Vessel-Guard/issues/new?template=feature_request.md)

## 🎉 You're Ready!

Congratulations! You now have a fully functional Vessel Guard development environment. 

### Next Steps:
1. 🧪 **Explore** the demo data and sample calculations
2. 📚 **Read** the [User Guide](./docs/USER_GUIDE.md) for detailed features
3. 🔧 **Customize** the platform for your organization's needs
4. 🚀 **Deploy** to your production environment

---

**Need help?** Check our [complete documentation](./docs/) or [create an issue](https://github.com/ahmed-hesham07/Vessel-Guard/issues) for support.

Happy engineering! 🚀⚙️
