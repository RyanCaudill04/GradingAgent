# CSCE-247 Grading Agent API

FastAPI backend service for automatically grading CSCE-247 design pattern individual assignments. This system analyzes student GitHub repositories and provides automated grading based on predefined criteria.

## 🎯 Purpose

This API service is designed for CSCE-247 Teaching Assistants to automate the grading process for individual design pattern assignments. Students submit their work via GitHub repository links, and the system automatically evaluates their code against established criteria.

## 🏗️ Architecture

- **Framework**: FastAPI with Python 3.11
- **Database**: PostgreSQL (shared with Django frontend)
- **Authentication**: GitHub token-based repository access
- **Grading Engine**: Automated analysis of design patterns and code structure
- **Storage**: Persistent grading results and criteria storage

## 🚀 Quick Start

### Docker (Recommended)
```bash
# From project root
docker-compose up --build -d
# API will be available at http://localhost:8001
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_SERVER=localhost
export POSTGRES_DB=postgres
export POSTGRES_PORT=5432

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📚 API Documentation

### Core Endpoints

#### `POST /assignments`
Create a new assignment configuration.

**Request:**
```json
{
  "assignment_name": "Strategy Pattern Assignment"
}
```

**Response:**
```json
{
  "message": "Assignment created successfully",
  "assignment_name": "Strategy Pattern Assignment"
}
```

#### `POST /assignments/{assignment_name}/criteria`
Upload grading criteria for an assignment.

**Request:**
- **Form Data**: `criteria_file` (File: .txt, .docx, or .json)

**Supported Formats:**
- **Text (.txt)**: Plain text grading rubric
- **Word (.docx)**: Formatted grading document
- **JSON (.json)**: Structured criteria with weights

**Response:**
```json
{
  "message": "Criteria uploaded successfully",
  "assignment_name": "Strategy Pattern Assignment",
  "file_type": "docx"
}
```

#### `POST /grade`
Submit a repository for automated grading.

**Request:**
```json
{
  "assignment_name": "Strategy Pattern Assignment",
  "repo_link": "https://github.com/student/csce247-assignment",
  "token": "ghp_xxxxxxxxxxxxxxxxxxxx"
}
```

**Response:**
```json
{
  "student_name": "john_doe",
  "assignment_name": "Strategy Pattern Assignment",
  "final_grade": 85.5,
  "max_points": 100,
  "grading_details": {
    "pattern_implementation": {
      "score": 30,
      "max_score": 35,
      "feedback": "Strategy pattern correctly implemented with minor issues..."
    },
    "code_quality": {
      "score": 25,
      "max_score": 30,
      "feedback": "Good code structure and documentation..."
    }
  },
  "submission_time": "2024-09-22T15:30:00Z"
}
```

#### `GET /grades`
Retrieve all grading results.

**Response:**
```json
[
  {
    "id": 1,
    "student_name": "john_doe",
    "assignment_name": "Strategy Pattern Assignment",
    "final_grade": 85.5,
    "submission_time": "2024-09-22T15:30:00Z"
  }
]
```

#### `GET /grades/{student_name}`
Get all grades for a specific student.

**Response:**
```json
[
  {
    "id": 1,
    "student_name": "john_doe",
    "assignment_name": "Strategy Pattern Assignment",
    "final_grade": 85.5,
    "assignment_details": { /* full grading breakdown */ }
  }
]
```

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "message": "FastAPI is connected!"
}
```

## 🧪 Testing

Run the test suite:
```bash
# With Docker
docker-compose exec fastapi python -m pytest

# Local development
pytest tests/
```

## 🗃️ Database Schema

### GradingResult Table
- `id`: Primary key
- `student_name`: Extracted from GitHub repository
- `assignment_name`: Reference to assignment
- `repo_link`: GitHub repository URL
- `final_grade`: Calculated final score
- `max_points`: Total possible points
- `grading_details`: JSON field with detailed breakdown
- `submission_time`: Timestamp of grading request
- `created_at`: Record creation time

### Assignment Table
- `id`: Primary key
- `assignment_name`: Unique assignment identifier
- `criteria`: JSON field with grading criteria
- `created_at`: Assignment creation time

## 🔧 Configuration

### Environment Variables
- `ENV`: Environment (development/production)
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_SERVER`: Database host
- `POSTGRES_DB`: Database name
- `POSTGRES_PORT`: Database port
- `ALLOWED_ORIGINS`: CORS allowed origins

### Grading Configuration
The grading engine can be configured through criteria files to evaluate:
- Design pattern implementation correctness
- Code quality and structure
- Documentation completeness
- Test coverage
- Repository organization

## 🔍 Logging and Monitoring

The API includes comprehensive logging for:
- Grading requests and results
- Repository access attempts
- Database operations
- Error tracking and debugging

## 🤝 Integration with Frontend

This API integrates seamlessly with the Django frontend service, providing:
- RESTful endpoints for all grading operations
- CORS configuration for web interface access
- Shared PostgreSQL database for data consistency
- Real-time grading status updates

## 📋 For TAs

### Common Workflows

1. **Setup New Assignment**:
   ```bash
   curl -X POST http://localhost:8001/assignments \
     -H "Content-Type: application/json" \
     -d '{"assignment_name": "Observer Pattern"}'
   ```

2. **Upload Grading Criteria**:
   Use the web interface at http://localhost:8000/upload-criteria/

3. **Batch Grade Submissions**:
   Students submit via web interface, results stored automatically

4. **Export Grades**:
   Access via web interface or direct API calls to `/grades`

### Troubleshooting

- **Repository Access Issues**: Verify GitHub token has read access
- **Grading Failures**: Check criteria file format and assignment name
- **Database Connection**: Ensure PostgreSQL is running and accessible

## 🔗 Related Services

- **Frontend**: Django web interface for TAs and students
- **Database**: PostgreSQL for persistent storage
- **Admin Interface**: pgAdmin for database management