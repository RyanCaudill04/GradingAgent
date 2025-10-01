# CSCE-247 Automated Grading System

An automated grading system for CSCE-247 design pattern assignments using AI-powered code analysis with Google Gemini API.

## 🎯 Overview

This system allows Teaching Assistants to automatically grade student Java assignments by analyzing GitHub repositories. It combines regex-based checks for specific violations (like using built-in methods) with AI-powered analysis using Google Gemini for evaluating design patterns, code quality, and adherence to rubrics.

## 🏗️ Architecture

- **Frontend**: Django web interface for TAs and students
- **Backend**: FastAPI service with Gemini API integration
- **Database**: PostgreSQL for storing assignments, criteria, and grades
- **AI Engine**: Google Gemini 1.5 Flash for intelligent code evaluation

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Gemini API key (TAs need their own keys)

### Start the System
```bash
# Build and start all services
make up

# Or manually:
docker-compose up --build -d

# Check status
make status
```

Services will be available at:
- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **pgAdmin**: http://localhost:5050
- **Database**: localhost:5432

## 📋 How to Use

### For Teaching Assistants

#### 1. Create an Assignment
```bash
curl -X POST http://localhost:8001/assignments \
  -H "Content-Type: application/json" \
  -d '{"assignment_name": "BinarySearch"}'
```

#### 2. Upload Grading Criteria

Create a criteria file in JSON format:
```json
{
  "natural_language_rubric": "Grade the binary search implementation...",
  "regex_checks": [
    {
      "pattern": "Arrays\\.binarySearch",
      "deduction": 50,
      "message": "Used built-in Arrays.binarySearch()"
    }
  ]
}
```

Upload via API:
```bash
curl -X POST http://localhost:8001/assignments/BinarySearch/criteria \
  -F "criteria_file=@criteria.json"
```

Or use the web interface at http://localhost:8000/upload-criteria/

#### 3. Grade a Student Submission

```bash
curl -X POST http://localhost:8001/grade \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_name": "BinarySearch",
    "repo_link": "https://github.com/student/csce247",
    "token": "ghp_your_github_token",
    "gemini_api_key": "your_gemini_api_key"
  }'
```

Or use the web interface at http://localhost:8000/grade/

### For Students

1. Push your assignment to a GitHub repository
2. Ensure your repository has a folder matching the assignment name (e.g., `BinarySearch/`)
3. All Java files in that folder will be graded
4. Submit your repository URL to your TA

## 🤖 How Grading Works

### Two-Phase Grading Process

1. **Regex Checks** (Automatic Deductions)
   - Fast pattern matching for specific violations
   - Example: Detecting use of built-in methods like `Arrays.binarySearch()`
   - Each violation results in immediate point deduction

2. **Gemini AI Analysis** (Intelligent Evaluation)
   - Evaluates design patterns and architecture
   - Assesses code quality and best practices
   - Checks for edge case handling
   - Reviews documentation and comments
   - Provides detailed, constructive feedback

### Grading Output Format

```
GRADE: 85/100

==================================================
DEDUCTIONS:
  [-10 points] Missing edge case handling for empty arrays
  [-5 points] Insufficient JavaDoc comments on public methods

==================================================
DETAILED FEEDBACK:
The binary search implementation is generally correct and achieves
O(log n) time complexity. However, the code lacks proper handling
of edge cases...
```

## 📁 Criteria File Format

### JSON Format (Recommended)
```json
{
  "natural_language_rubric": "Detailed grading instructions for AI...",
  "regex_checks": [
    {
      "pattern": "regex pattern",
      "deduction": 10,
      "message": "Description of the violation"
    }
  ]
}
```

### Text/Word Format
- `.txt` or `.docx` files are treated as natural language rubrics only
- No regex checks are applied
- Entire content is sent to Gemini for interpretation

## 🔑 Getting a Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key
4. Keep it secure - treat it like a password

**Note**: Each TA provides their own API key when grading. This ensures:
- Cost control and accountability
- No shared rate limits
- Individual usage tracking

## 🛠️ Development

### Makefile Commands
```bash
make build          # Build all services
make up            # Start services
make down          # Stop services
make logs          # View all logs
make logs-fastapi  # View backend logs
make logs-django   # View frontend logs
make status        # Show service status
make test          # Run tests
make migrate       # Run database migrations
make clean         # Remove all containers and volumes
```

### Running Tests
```bash
# Run all tests
make test

# Or manually:
docker-compose exec fastapi python -m pytest
docker-compose exec django python manage.py test
```

### Database Migrations

After modifying database models, create and run migrations:

```bash
# For FastAPI (using Alembic - to be set up)
docker-compose exec fastapi alembic revision --autogenerate -m "Description"
docker-compose exec fastapi alembic upgrade head

# For Django
docker-compose exec django python manage.py makemigrations
docker-compose exec django python manage.py migrate
```

## 📊 API Endpoints

### Assignments
- `POST /assignments` - Create new assignment
- `POST /assignments/{name}/criteria` - Upload grading criteria

### Grading
- `POST /grade` - Grade a student submission
  ```json
  {
    "assignment_name": "string",
    "repo_link": "https://github.com/user/repo",
    "token": "github_token",
    "gemini_api_key": "gemini_key"
  }
  ```

### Results
- `GET /grades` - Get all grading results
- `GET /grades/{student_name}` - Get grades for specific student

Full API documentation: http://localhost:8001/docs

## 🔒 Security Notes

- GitHub tokens are used only for cloning repositories and are not stored
- Gemini API keys are not stored in the database
- All file operations occur in temporary directories that are automatically cleaned
- Input validation on all API endpoints
- CORS configured for frontend-backend communication

## 🐛 Troubleshooting

### Repository Clone Fails
- Verify the GitHub token has read access to the repository
- Check if the repository is private and token has appropriate permissions
- Ensure repository URL is correct

### Gemini API Errors
- Verify your API key is valid
- Check if you've exceeded rate limits
- Ensure you have billing enabled (if required)

### Assignment Folder Not Found
- Ensure the repository has a folder with exact name matching the assignment
- Folder names are case-sensitive

### No Java Files Found
- Verify `.java` files exist in the assignment folder
- Check file extensions are lowercase `.java`

## 📦 Project Structure

```
Grader/
├── GradingAgentAPI/          # FastAPI backend
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Configuration
│   │   ├── db/               # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic
│   ├── tests/                # Tests
│   └── requirements.txt
├── GradingAgentFrontend/     # Django frontend
│   └── AgentDeployer/        # Django app
├── docker-compose.yml        # Production compose
├── docker-compose.dev.yml    # Development compose
├── Makefile                  # Development commands
└── README.md                 # This file
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests for new functionality
4. Run `make test` to ensure all tests pass
5. Submit a pull request

## 📄 License

This project is for academic use in CSCE-247 at the University of South Carolina.

## 🆘 Support

For issues or questions:
- Check the troubleshooting section above
- Review logs: `make logs`
- Check service status: `make status`
- Contact the course TAs or instructor
