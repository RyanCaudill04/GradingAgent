# CSCE-247 Grading Agent Frontend

Django web interface for CSCE-247 Teaching Assistants to manage automated grading of design pattern individual assignments. This frontend provides an intuitive interface for TAs to upload grading criteria, monitor submissions, and review results.

## 🎯 Purpose

This web application serves as the primary interface for CSCE-247 TAs to:
- Manage assignment grading criteria
- Monitor student GitHub repository submissions
- Review automated grading results
- Track submission history and student progress
- Export grades for gradebook integration

## 🏗️ Architecture

- **Framework**: Django 5.2.4 with Python 3.11
- **Database**: PostgreSQL (shared with FastAPI backend)
- **Frontend**: Server-side rendered HTML with CSS styling
- **API Integration**: RESTful communication with FastAPI backend
- **Authentication**: Built-in Django admin for TA access

## 🚀 Quick Start

### Docker (Recommended)
```bash
# From project root
docker-compose up --build -d
# Web interface available at http://localhost:8000
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FASTAPI_URL=http://localhost:8001
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_SERVER=localhost
export POSTGRES_DB=postgres
export POSTGRES_PORT=5432

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start development server
python manage.py runserver 0.0.0.0:8000
```

## 🖥️ User Interface

### Main Dashboard (`/`)
- Welcome screen with navigation to key features
- Quick access to upload criteria and submit grading requests
- Clean, TA-friendly interface design

### Upload Grading Criteria (`/upload-criteria/`)
**For TAs to set up new assignments**
- Upload grading rubrics (.txt, .docx, .json formats)
- Specify assignment names and criteria
- Preview and validate uploaded criteria

**Usage:**
1. Enter assignment name (e.g., "Strategy Pattern Assignment")
2. Upload criteria file containing grading rubric
3. System validates and stores criteria for automated grading

### Submit Grading Request (`/grade/`)
**For processing student GitHub submissions**
- Input GitHub repository URL
- Specify assignment name
- Provide GitHub access token
- Real-time grading progress tracking

**Workflow:**
1. Student provides GitHub repository link
2. TA enters repository URL and assignment name
3. System clones and analyzes repository
4. Automated grading results displayed immediately

### View Grades (`/grades/`)
**Grade management and review interface**
- Browse all assignments and submissions
- Filter by assignment or student name
- Sort by submission time, grade, or student name
- Export functionality for gradebook integration

### Submission History (`/submissions/`)
**Comprehensive submission tracking**
- Complete submission history with timestamps
- Status tracking (Pending, Completed, Failed)
- Detailed grading breakdowns
- Student-specific grade histories

## 📋 Features for TAs

### Assignment Management
- **Create Assignments**: Set up new design pattern assignments
- **Upload Criteria**: Define automated grading rubrics
- **Manage Submissions**: Track and review all student submissions

### Grading Workflow
1. **Setup Phase**:
   - Upload assignment criteria via web interface
   - Define grading parameters and weights

2. **Submission Phase**:
   - Students submit GitHub repository links
   - System automatically processes submissions
   - Real-time status updates for TAs

3. **Review Phase**:
   - Browse all submissions by assignment
   - Review detailed grading breakdowns
   - Export grades for official gradebooks

### Batch Operations
- Process multiple submissions simultaneously
- Bulk export of grades by assignment
- Historical data analysis and reporting

## 🗃️ Data Management

### Submission Tracking
Each submission includes:
- **Student Information**: Name extracted from GitHub
- **Repository Details**: URL, submission timestamp
- **Grading Results**: Detailed breakdown with feedback
- **Status Tracking**: Pending → Processing → Completed/Failed

### Grade Storage
Persistent storage in PostgreSQL includes:
- Individual assignment scores
- Detailed grading criteria evaluation
- Historical submission data
- Student progress tracking

## 🔧 Configuration

### Environment Variables
- `FASTAPI_URL`: Backend API endpoint (default: http://fastapi:8001)
- `POSTGRES_*`: Database connection parameters
- `DEBUG`: Development mode toggle
- `SECRET_KEY`: Django security key

### Static Files
Static assets served via WhiteNoise for production deployment:
- CSS styling for clean TA interface
- Form validation and user feedback
- Responsive design for various screen sizes

## 🧪 Testing

Run the Django test suite:
```bash
# With Docker
docker-compose exec django python manage.py test

# Local development
python manage.py test AgentDeployer
```

### Test Coverage
- View functionality and form handling
- API integration with FastAPI backend
- Database operations and data integrity
- User interface components

## 🔐 Security Features

### Access Control
- Django admin interface for TA management
- CSRF protection on all forms
- Secure handling of GitHub tokens
- Input validation and sanitization

### Data Protection
- Encrypted database connections
- Secure static file serving
- Protection against common web vulnerabilities

## 🤝 API Integration

### Backend Communication
The frontend communicates with the FastAPI backend through:
- **Assignment Creation**: POST requests to create new assignments
- **Criteria Upload**: File upload handling for grading rubrics
- **Grading Requests**: Submission processing coordination
- **Data Retrieval**: Grade and submission history queries

### Error Handling
Comprehensive error handling for:
- Backend service unavailability
- Invalid repository URLs or tokens
- Network timeouts and connectivity issues
- Malformed grading criteria files

## 📊 Reporting and Analytics

### Grade Export
- CSV export functionality for gradebook integration
- Detailed submission reports for academic records
- Student progress tracking across assignments

### Submission Analytics
- Assignment completion rates
- Average grading scores by assignment type
- Common grading issues and patterns

## 🎓 CSCE-247 Specific Features

### Design Pattern Focus
Optimized for evaluating:
- **Strategy Pattern**: Implementation correctness and usage
- **Observer Pattern**: Event handling and notification systems
- **Factory Pattern**: Object creation and abstraction
- **Decorator Pattern**: Dynamic behavior modification
- **MVC Pattern**: Separation of concerns and architecture

### Academic Integration
- Semester-based assignment organization
- Student roster management
- Grade submission to university systems
- Academic integrity monitoring

## 🚀 Deployment

### Production Setup
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.yml up --build -d

# Run migrations in production
docker-compose exec django python manage.py migrate

# Create superuser for admin access
docker-compose exec django python manage.py createsuperuser
```

### Admin Interface
Access Django admin at `/admin/` to:
- Manage TA user accounts
- Review submission data
- Configure system settings
- Monitor application health

## 🔗 Related Services

- **Backend API**: FastAPI service for grading logic
- **Database**: PostgreSQL for data persistence
- **Admin Tools**: pgAdmin for database management
- **Development**: Hot reload and debugging support

## 📋 TA Quick Reference

### Daily Operations
1. **Check New Submissions**: Visit `/submissions/` for recent activity
2. **Review Grades**: Use `/grades/` to browse results by assignment
3. **Upload New Criteria**: Use `/upload-criteria/` for new assignments
4. **Export Grades**: Generate CSV files for gradebook updates

### Troubleshooting
- **Grading Failures**: Check repository accessibility and criteria files
- **Missing Students**: Verify GitHub usernames and repository permissions
- **Grade Discrepancies**: Review detailed grading breakdowns in submission detail views

### Best Practices
- Upload criteria before assignment deadlines
- Regularly export grades for backup
- Monitor submission patterns for academic integrity
- Provide clear GitHub repository requirements to students