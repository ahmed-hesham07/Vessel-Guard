# Vessel Guard User Guide

## 🎯 **Complete Guide for Engineers**

Welcome to Vessel Guard - your comprehensive platform for pressure vessel analysis, piping calculations, and engineering compliance. This guide will help you master the platform and streamline your engineering workflows.

---

## 🚀 **Getting Started**

### **1. Account Setup**

#### **Creating Your Account**
1. Navigate to [vessel-guard.com](https://vessel-guard.com)
2. Click "Sign Up" and choose your plan
3. Enter your professional email and create a secure password
4. Verify your email address
5. Complete your engineering profile

#### **Organization Setup**
If you're the first user from your company:
1. Go to **Settings** → **Organization**
2. Enter company information and address
3. Upload company logo (optional)
4. Set default engineering units and standards
5. Invite team members via email

#### **Profile Configuration**
1. Navigate to **Profile** → **Settings**
2. Set your preferred:
   - Engineering units (Imperial/Metric)
   - Default standards (ASME, EN, API)
   - Time zone and language
   - Notification preferences

### **2. Dashboard Overview**

Your dashboard provides a comprehensive view of your engineering work:

#### **Key Metrics Cards**
- **Active Projects**: Currently ongoing projects
- **Pending Calculations**: Calculations waiting for review
- **Recent Reports**: Latest generated compliance reports
- **Team Activity**: Recent actions by your team

#### **Quick Actions**
- **New Project**: Start a new engineering project
- **Quick Calculation**: Run a single calculation
- **Import Data**: Upload existing project data
- **Generate Report**: Create compliance documentation

---

## 📋 **Project Management**

### **Creating Your First Project**

#### **Step 1: Project Setup**
1. Click **"New Project"** from dashboard
2. Enter project details:
   ```
   Project Name: "Refinery Expansion - Phase 1"
   Project Code: "REF-2024-001" 
   Description: "Pressure vessel analysis for new refinery units"
   Start Date: Current date
   End Date: Project completion target
   ```
3. Select applicable standards:
   - ✅ ASME VIII Division 1
   - ✅ ASME B31.3 Process Piping
   - ✅ API 579 Fitness-for-Service
4. Click **"Create Project"**

#### **Step 2: Project Organization**
```
Project Structure:
├── Project Overview
├── Vessels (Equipment List)
├── Calculations (Analysis Results)
├── Reports (Compliance Documents)
├── Files (Supporting Documents)
└── Team (Project Members)
```

#### **Step 3: Team Collaboration**
1. Go to **Project** → **Team**
2. Click **"Invite Members"**
3. Enter team member emails
4. Assign roles:
   - **Project Lead**: Full project access
   - **Engineer**: Calculation and design access
   - **Reviewer**: Review and approval access
   - **Viewer**: Read-only access

### **Project Templates**

Use pre-configured templates for common project types:

#### **Pressure Vessel Project Template**
- Pre-configured for ASME VIII compliance
- Standard vessel types and parameters
- Common calculation workflows
- Compliance report templates

#### **Piping System Project Template**
- ASME B31.3 process piping setup
- Standard pipe sizes and materials
- Stress analysis workflows
- Piping isometric integration

#### **Refinery Project Template**
- Multi-unit refinery configuration
- API standards integration
- Fitness-for-service evaluations
- Comprehensive reporting suite

---

## 🏗️ **Vessel Management**

### **Adding Vessels to Your Project**

#### **Single Vessel Entry**
1. Navigate to **Project** → **Vessels**
2. Click **"Add Vessel"**
3. Enter vessel identification:
   ```
   Tag Number: V-101
   Name: Main Reactor Vessel
   Service: Hydrocracker Reactor
   Location: Unit 100, Elevation 150'
   ```

#### **Vessel Design Parameters**
```
Design Conditions:
├── Design Pressure: 1500 psig
├── Design Temperature: 750°F
├── Operating Pressure: 1350 psig
├── Operating Temperature: 725°F
├── External Pressure: 15 psia
└── Hydrostatic Test: 2250 psig

Physical Dimensions:
├── Inside Diameter: 48 inches
├── Overall Length: 120 feet
├── Shell Thickness: 2.5 inches
├── Head Type: 2:1 Ellipsoidal
└── Head Thickness: 2.5 inches

Material Specifications:
├── Shell Material: SA-516 Grade 70
├── Head Material: SA-516 Grade 70
├── Corrosion Allowance: 0.125 inches
├── Joint Efficiency: 1.0 (RT-1)
└── Post Weld Heat Treatment: Yes
```

#### **Bulk Vessel Import**
For large projects with many vessels:

1. Download the **Vessel Import Template**
2. Fill in vessel data in Excel format
3. Click **"Import Vessels"** → **"Upload File"**
4. Review and validate imported data
5. Click **"Confirm Import"**

**Template Structure:**
| Tag Number | Name | Type | Design Pressure | Design Temp | Material | Diameter | Thickness |
|------------|------|------|----------------|-------------|----------|----------|-----------|
| V-101 | Reactor | pressure_vessel | 1500 | 750 | SA-516-70 | 48 | 2.5 |
| V-102 | Separator | pressure_vessel | 600 | 350 | SA-516-70 | 36 | 1.5 |

### **Vessel Documentation**

#### **Uploading Design Documents**
1. Select vessel from project
2. Go to **Documents** tab
3. Upload relevant files:
   - P&ID drawings
   - Vessel data sheets
   - Material certificates
   - Previous inspection reports
   - Manufacturer drawings

#### **Vessel Inspection History**
Track inspection and maintenance history:
1. Navigate to **Vessel** → **Inspections**
2. Click **"Add Inspection"**
3. Enter inspection details:
   ```
   Inspection Date: 2024-01-15
   Inspector: John Smith, API 510
   Inspection Type: External Visual
   Condition: Good
   Findings: Minor surface corrosion on support pads
   Recommendations: Monitor and recoat supports
   Next Inspection: 2026-01-15
   ```

---

## 🧮 **Engineering Calculations**

### **Pressure Vessel Calculations**

#### **ASME VIII Division 1 Analysis**

**Step 1: Create New Calculation**
1. Select your vessel
2. Click **"New Calculation"**
3. Choose **"ASME VIII Division 1"**

**Step 2: Input Parameters**
```
Design Data:
├── Design Pressure: 1500 psig
├── Design Temperature: 750°F
├── Corrosion Allowance: 0.125 in
└── Joint Efficiency: 1.0

Geometry:
├── Inside Diameter: 48 inches
├── Shell Thickness: 2.5 inches
├── Head Type: 2:1 Ellipsoidal
└── Head Thickness: 2.5 inches

Material:
├── Material: SA-516 Grade 70
├── Allowable Stress (750°F): 17,500 psi
├── Yield Strength: 38,000 psi
└── Tensile Strength: 70,000 psi
```

**Step 3: Review Results**
```
Calculation Results:
├── Required Shell Thickness: 2.18 inches
├── Actual Shell Thickness: 2.50 inches
├── Safety Margin: 14.6%
├── Maximum Allowable Working Pressure: 1,682 psig
├── Hydrostatic Test Pressure: 2,250 psig
└── Compliance Status: ✅ COMPLIANT

Critical Checks:
├── ✅ Shell thickness adequate
├── ✅ Head thickness adequate  
├── ✅ Material suitable for temperature
├── ✅ Weld joint efficiency acceptable
└── ✅ Corrosion allowance sufficient
```

#### **Advanced Calculations**

**Fitness-for-Service (API 579)**
For existing vessels with flaws or degradation:

1. Choose **"API 579 Assessment"**
2. Input current conditions:
   ```
   Current Thickness: 2.25 inches (after corrosion)
   Flaw Description: Localized thinning area
   Flaw Dimensions: 6" x 4" x 0.25" deep
   Assessment Level: Level 2
   ```
3. Review fitness evaluation:
   ```
   Assessment Results:
   ├── Remaining Life: 8.5 years
   ├── Safe Operating Envelope: 1350 psig @ 725°F
   ├── Recommended Action: Continue operation
   └── Next Inspection: 2026-01-15
   ```

### **Piping System Calculations**

#### **ASME B31.3 Process Piping**

**Step 1: Define Piping System**
```
Line Identification: 6"-P-101-HC-150#
Service: Heavy Hydrocarbon
Design Conditions: 150 psig @ 400°F
Pipe Size: 6" NPS Schedule 40
Material: A106 Grade B
```

**Step 2: Stress Analysis**
```
Loading Conditions:
├── Internal Pressure: 150 psig
├── Thermal Expansion: 400°F operating
├── Dead Weight: Pipe + fluid + insulation
├── Live Loads: Wind, seismic (per local codes)
└── Support Reactions: Fixed, guided, spring hangers
```

**Step 3: Review Results**
```
Stress Analysis Results:
├── Sustained Stress: 8,500 psi (< 20,000 psi allowable) ✅
├── Displacement Stress: 15,200 psi (< 30,000 psi allowable) ✅
├── Maximum Support Load: 2,850 lbs
├── Critical Stress Location: Nozzle connection
└── Compliance Status: ✅ COMPLIANT
```

### **Calculation Validation**

#### **Engineering Review Process**
1. **Initial Calculation**: Performed by design engineer
2. **Peer Review**: Checked by senior engineer
3. **Approval**: Signed off by responsible engineer
4. **Documentation**: Saved to project records

#### **Calculation Quality Checks**
```
Automated Checks:
├── ✅ Input parameter validation
├── ✅ Unit consistency verification
├── ✅ Code compliance verification
├── ✅ Result reasonableness check
└── ✅ Safety factor validation

Manual Review Points:
├── 🔍 Design basis assumptions
├── 🔍 Material property verification
├── 🔍 Load case completeness
├── 🔍 Code interpretation accuracy
└── 🔍 Result documentation quality
```

---

## 📊 **Report Generation**

### **Compliance Reports**

#### **Creating an ASME Compliance Report**

**Step 1: Report Setup**
1. Navigate to **Project** → **Reports**
2. Click **"Generate Report"**
3. Select **"ASME Compliance Report"**
4. Configure report scope:
   ```
   Report Title: "Pressure Vessel Compliance Analysis"
   Project: REF-2024-001
   Vessels: V-101, V-102, V-103
   Calculations: All ASME VIII calculations
   Review Period: 2024 Design Phase
   ```

**Step 2: Report Sections**
Select sections to include:
```
✅ Executive Summary
✅ Project Overview
✅ Design Basis and Criteria
✅ Vessel Specifications
✅ Material Certifications
✅ Calculation Summary
✅ Code Compliance Analysis
✅ Safety Assessment
✅ Recommendations
✅ Appendices (detailed calculations)
```

**Step 3: Report Customization**
```
Formatting Options:
├── Company Logo and Branding
├── Professional Report Template
├── Custom Cover Page
├── Table of Contents
├── Executive Summary
└── Digital Signatures

Output Formats:
├── 📄 PDF (recommended for compliance)
├── 📊 Excel (for data analysis)
├── 🌐 Interactive Web Report
└── 📧 Email Distribution
```

#### **Report Review and Approval**

**Review Workflow:**
1. **Draft Review**: Internal team review
2. **Technical Review**: Senior engineer approval
3. **Client Review**: Customer feedback cycle
4. **Final Approval**: Authorized engineer signature
5. **Distribution**: Send to stakeholders

**Digital Signatures:**
```
Signature Block:
├── Engineer Name: John Smith, P.E.
├── License Number: PE-12345 (State)
├── Date Signed: 2024-01-21
├── Digital Certificate: SHA-256 encrypted
└── Signature Purpose: Design verification
```

### **Custom Report Templates**

#### **Creating Custom Templates**
1. Go to **Settings** → **Report Templates**
2. Click **"Create Template"**
3. Design template structure:
   ```
   Template Sections:
   ├── Cover Page (company branding)
   ├── Document Control (revisions)
   ├── Table of Contents (auto-generated)
   ├── Introduction (project background)
   ├── Technical Content (calculations)
   ├── Conclusions (engineering summary)
   └── Appendices (supporting data)
   ```

#### **Template Variables**
Use dynamic variables in templates:
```
{{project.name}} - Project name
{{project.code}} - Project code
{{vessel.tag_number}} - Vessel tag
{{calculation.result.compliance_status}} - Result
{{engineer.name}} - Engineer name
{{current_date}} - Current date
{{company.name}} - Company name
```

---

## 👥 **Team Collaboration**

### **Project Sharing and Permissions**

#### **User Role Definitions**
```
Project Owner:
├── Full project management
├── Team member management
├── Calculation approval authority
├── Report generation and distribution
└── Project settings configuration

Senior Engineer:
├── All calculations and analysis
├── Calculation review and approval
├── Report review and approval
├── Mentor junior engineers
└── Quality assurance oversight

Engineer:
├── Create and modify calculations
├── Generate technical reports
├── Upload project documents
├── Review team calculations
└── Participate in design reviews

Junior Engineer:
├── Create basic calculations
├── Assist with data collection
├── Generate draft reports
├── Learn from senior engineers
└── Participate in training

Reviewer:
├── Review calculations and reports
├── Provide technical feedback
├── Approve final deliverables
├── Sign off on compliance
└── External stakeholder interface

Viewer:
├── Read-only access to project
├── Download approved reports
├── View calculation results
├── Access project documents
└── Participate in presentations
```

#### **Permission Management**
1. Navigate to **Project** → **Team** → **Permissions**
2. Set granular permissions per user:
   ```
   Calculation Permissions:
   ├── Create calculations: ✅
   ├── Modify calculations: ✅
   ├── Delete calculations: ❌
   ├── Approve calculations: ✅
   └── Export results: ✅

   Report Permissions:
   ├── Generate reports: ✅
   ├── Modify templates: ❌
   ├── Approve reports: ✅
   ├── Distribute reports: ❌
   └── Digital signature: ✅
   ```

### **Real-Time Collaboration**

#### **Live Collaboration Features**
```
Real-Time Updates:
├── 👁️ See who's viewing/editing
├── 💬 In-app messaging and comments
├── 🔔 Instant notifications
├── 📝 Change tracking and history
└── 🔄 Auto-save and sync
```

#### **Communication Tools**
1. **Project Comments**: Discussion threads on calculations
2. **Task Assignments**: Assign work to team members
3. **Status Updates**: Project milestone tracking
4. **Review Requests**: Formal calculation reviews
5. **Notifications**: Email and in-app alerts

### **Version Control**

#### **Calculation Versioning**
Every calculation maintains complete version history:
```
Version History:
├── v1.0 - Initial calculation (John Smith, 2024-01-15)
├── v1.1 - Updated material properties (Mary Jones, 2024-01-16) 
├── v1.2 - Revised pressure rating (John Smith, 2024-01-17)
├── v2.0 - Design change incorporation (Mary Jones, 2024-01-18)
└── v2.1 - Final approval (Bob Wilson, 2024-01-19)

Change Tracking:
├── 📝 What changed: Field-level tracking
├── 👤 Who changed it: User attribution
├── ⏰ When changed: Timestamp
├── 💬 Why changed: Comment requirement
└── 🔍 Impact analysis: Affected calculations
```

#### **Document Management**
```
Document Control:
├── 📁 Centralized file repository
├── 🔐 Access control and permissions
├── 📋 Check-in/check-out system
├── 🏷️ Metadata and tagging
└── 🔍 Advanced search capabilities
```

---

## 🔍 **Advanced Features**

### **Data Import and Export**

#### **Importing Existing Data**
```
Supported Import Formats:
├── 📊 Excel/CSV files
├── 📄 PDF data extraction
├── 🔧 CAD file integration
├── 📋 Legacy system data
└── 🌐 API integrations

Import Workflows:
├── Data validation and cleansing
├── Unit conversion and standardization
├── Duplicate detection and merging
├── Error reporting and correction
└── Batch processing for large datasets
```

#### **Data Export Options**
```
Export Formats:
├── 📊 Excel/CSV (data analysis)
├── 📄 PDF (documentation)
├── 📋 XML (system integration)
├── 🔌 API (real-time access)
└── 📂 ZIP (complete project package)

Export Configurations:
├── Custom field selection
├── Data filtering and grouping
├── Format customization
├── Automated scheduling
└── Secure delivery options
```

### **Integration Capabilities**

#### **Third-Party Tool Integration**
```
CAD Software:
├── AutoCAD Plant 3D
├── AVEVA PDMS/E3D
├── Bentley AutoPLANT
├── Intergraph SmartPlant
└── SolidWorks/Inventor

Analysis Software:
├── ANSYS mechanical analysis
├── Caesar II piping stress
├── PV Elite pressure vessel
├── Compress pressure vessel
└── AutoPIPE piping analysis

Document Management:
├── SharePoint integration
├── Box/Dropbox sync
├── Google Drive integration
├── Documentum connection
└── Custom API integration
```

#### **API Integration**
For custom integrations and automation:
```python
# Example: Automated calculation workflow
import vessel_guard_api as vg

# Connect to API
client = vg.Client(api_key="your_key")

# Create project from CAD data
project = client.projects.create_from_cad("plant_model.dwg")

# Run batch calculations
for vessel in project.vessels:
    calc = client.calculations.create({
        "vessel_id": vessel.id,
        "type": "asme_viii_div1",
        "auto_parameters": True  # Extract from CAD
    })
    
    if calc.status == "completed":
        print(f"Vessel {vessel.tag}: {calc.compliance_status}")

# Generate compliance report
report = client.reports.generate({
    "project_id": project.id,
    "template": "asme_compliance",
    "auto_distribute": True
})
```

### **Mobile Access**

#### **Mobile App Features**
```
Field Access:
├── 📱 Native iOS/Android apps
├── 🔍 Project and vessel search
├── 📊 Calculation result viewing
├── 📸 Photo documentation
└── 🔔 Push notifications

Offline Capabilities:
├── 💾 Sync project data for offline access
├── 📷 Capture inspection photos offline
├── 📝 Create offline notes and comments
├── 🔄 Auto-sync when connected
└── 📊 View cached calculation results
```

---

## 🎓 **Training and Certification**

### **Platform Training**

#### **Getting Started Course**
```
Module 1: Platform Overview (30 min)
├── Interface navigation
├── Project structure
├── Basic calculations
└── Report generation

Module 2: Advanced Features (45 min) 
├── Complex calculations
├── Custom templates
├── Team collaboration
└── Data integration

Module 3: Best Practices (30 min)
├── Quality assurance
├── Documentation standards
├── Compliance workflows
└── Troubleshooting
```

#### **Certification Levels**
```
Certified User:
├── Basic platform proficiency
├── Standard calculation workflows
├── Report generation
└── 40 hours platform experience

Certified Power User:
├── Advanced calculation techniques
├── Custom template creation
├── Team leadership
└── 100 hours platform experience

Certified Administrator:
├── Organization management
├── User training capability
├── Advanced integrations
└── 200 hours platform experience
```

### **Engineering Standards Training**

#### **ASME Compliance Training**
```
ASME VIII Pressure Vessels:
├── Code requirements and interpretations
├── Material selection and properties
├── Design calculation methodologies
├── Inspection and testing requirements
└── Documentation and certification

ASME B31.3 Process Piping:
├── Scope and applicability
├── Design conditions and loads
├── Stress analysis requirements
├── Material and component standards
└── Installation and examination
```

---

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### **Calculation Errors**
```
Issue: "Material not found in database"
Solution:
├── 1. Check material specification spelling
├── 2. Use standard ASME/ASTM designations
├── 3. Contact support for material additions
└── 4. Use similar material as temporary solution

Issue: "Input parameters out of range"
Solution:
├── 1. Verify unit consistency (psi vs bara)
├── 2. Check for reasonable engineering values
├── 3. Review design conditions vs operating
└── 4. Consult applicable code limits
```

#### **Performance Issues**
```
Issue: Slow calculation processing
Solution:
├── 1. Break large projects into smaller chunks
├── 2. Use bulk operations for multiple items
├── 3. Optimize network connection
└── 4. Contact support for server status

Issue: Report generation timeout
Solution:
├── 1. Reduce report scope and complexity
├── 2. Generate sections separately
├── 3. Use simplified templates
└── 4. Schedule generation during off-peak hours
```

### **Getting Help**

#### **Support Channels**
```
Self-Service:
├── 📚 Knowledge base and FAQ
├── 🎥 Video tutorials
├── 📖 User documentation
├── 💬 Community forums
└── 🔍 Search help articles

Direct Support:
├── 📧 Email support (24-48 hour response)
├── 📞 Phone support (business hours)
├── 💬 Live chat (immediate response)
├── 🎯 Screen sharing sessions
└── 🏢 On-site training (enterprise)

Emergency Support:
├── 🚨 Critical issue hotline
├── ⚡ 4-hour response guarantee
├── 🔧 Direct engineer access
├── 📊 Priority escalation
└── 💼 Enterprise SLA coverage
```

#### **Best Practices for Support Requests**
```
Information to Include:
├── 📋 Detailed problem description
├── 🖼️ Screenshots of error messages
├── 📊 Sample calculation data
├── 🌐 Browser/device information
└── ⏰ Time when issue occurred

Steps to Take First:
├── 🔄 Refresh browser/restart app
├── 🧹 Clear browser cache
├── 🔍 Search knowledge base
├── 💾 Try with sample data
└── 📱 Test on different device
```

---

## 📈 **Continuous Improvement**

### **Staying Updated**

#### **Platform Updates**
```
Update Types:
├── 🐛 Bug fixes (automatic)
├── 🆕 New features (monthly)
├── 📋 Code updates (quarterly)
├── 🔒 Security patches (as needed)
└── 🎨 UI improvements (ongoing)

Notification Methods:
├── 📧 Email announcements
├── 🔔 In-app notifications
├── 📰 Release notes
├── 🎥 Feature demonstration videos
└── 📚 Updated documentation
```

#### **Training Updates**
```
Continuing Education:
├── 📅 Monthly webinar series
├── 🎓 Advanced technique workshops
├── 📋 New code interpretation sessions
├── 🤝 User conference (annual)
└── 🏆 Best practice sharing
```

### **Feedback and Suggestions**

#### **How to Provide Feedback**
1. **Feature Requests**: Use in-app feedback form
2. **Bug Reports**: Submit via support portal
3. **User Experience**: Participate in surveys
4. **Training Needs**: Contact training team
5. **Integration Requests**: Discuss with sales team

#### **Product Roadmap Participation**
```
User Input Opportunities:
├── 🗳️ Feature voting system
├── 💬 User advisory board
├── 🧪 Beta testing program
├── 📊 Usage analytics review
└── 🎯 Focus group participation
```

---

## 📞 **Support and Resources**

### **Contact Information**
- **Technical Support**: support@vessel-guard.com
- **Training Team**: training@vessel-guard.com  
- **Sales Team**: sales@vessel-guard.com
- **Emergency Hotline**: +1-800-VESSEL-1

### **Additional Resources**
- **User Community**: [community.vessel-guard.com](https://community.vessel-guard.com)
- **Video Tutorials**: [learn.vessel-guard.com](https://learn.vessel-guard.com)
- **Status Page**: [status.vessel-guard.com](https://status.vessel-guard.com)
- **Developer APIs**: [developers.vessel-guard.com](https://developers.vessel-guard.com)

---

*This guide is regularly updated based on user feedback and platform enhancements. Last updated: December 2024*