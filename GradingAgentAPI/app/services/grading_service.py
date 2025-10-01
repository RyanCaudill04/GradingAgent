from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.schemas.grading import GradingRequest, AssignmentCreate
from app.db import models
from app.schemas.grading_result import GradingResult as GradingResultSchema
import tempfile
import subprocess
import os
import json
import re
import docx
import google.generativeai as genai


async def create_assignment(request: AssignmentCreate, db: Session):
    db_assignment = db.query(models.Assignment).filter(models.Assignment.name == request.assignment_name).first()
    if db_assignment:
        raise HTTPException(status_code=400, detail="Assignment already exists")
    new_assignment = models.Assignment(name=request.assignment_name)
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment


async def save_criteria(assignment_name: str, criteria_file: UploadFile, db: Session):
    """
    Save grading criteria for an assignment.
    Expected format: JSON with 'natural_language_rubric' and optional 'regex_checks' array
    """
    assignment = db.query(models.Assignment).filter(models.Assignment.name == assignment_name).first()
    if not assignment:
        assignment = models.Assignment(name=assignment_name)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

    file_extension = criteria_file.filename.split('.')[-1]
    if file_extension not in ['txt', 'docx', 'json']:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt, .docx, and .json files are allowed.")

    # Read file content
    if file_extension == 'docx':
        try:
            doc = docx.Document(criteria_file.file)
            criteria_text = "\n".join([para.text for para in doc.paragraphs])
            # For .docx, treat entire content as natural language rubric
            criteria_data = {
                "natural_language_rubric": criteria_text,
                "regex_checks": []
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing .docx file: {e}")
    elif file_extension == 'json':
        try:
            criteria_text_bytes = await criteria_file.read()
            criteria_data = json.loads(criteria_text_bytes.decode("utf-8"))
            # Validate JSON structure
            if "natural_language_rubric" not in criteria_data:
                raise HTTPException(status_code=400, detail="JSON must contain 'natural_language_rubric' field")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")
    else:  # .txt
        criteria_text_bytes = await criteria_file.read()
        criteria_text = criteria_text_bytes.decode("utf-8")
        # For .txt, treat entire content as natural language rubric
        criteria_data = {
            "natural_language_rubric": criteria_text,
            "regex_checks": []
        }

    # Save to database
    criteria = db.query(models.Criteria).filter(models.Criteria.assignment_id == assignment.id).first()
    if criteria:
        criteria.natural_language_rubric = criteria_data["natural_language_rubric"]
        criteria.regex_checks = criteria_data.get("regex_checks", [])
    else:
        criteria = models.Criteria(
            assignment_id=assignment.id,
            natural_language_rubric=criteria_data["natural_language_rubric"],
            regex_checks=criteria_data.get("regex_checks", [])
        )
        db.add(criteria)

    db.commit()
    return {"message": f"Criteria for {assignment_name} saved."}


async def grade_assignment(request: GradingRequest, db: Session) -> dict:
    """
    Grade a student's assignment by:
    1. Cloning their GitHub repository
    2. Finding Java files in the assignment folder
    3. Running regex checks for automatic deductions
    4. Using Gemini API to evaluate code against natural language rubric
    """
    repo_url = str(request.repo_link)
    authenticated_url = repo_url.replace("https://", f"https://oauth2:{request.token}@")

    # Get assignment and criteria
    assignment = db.query(models.Assignment).filter(models.Assignment.name == request.assignment_name).first()
    if not assignment or not assignment.criteria:
        raise HTTPException(status_code=404, detail=f"Grading criteria for '{request.assignment_name}' not found.")

    # Extract student ID from repo URL (e.g., github.com/username/repo -> username)
    student_id = _extract_student_id(repo_url)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone repository
        try:
            subprocess.run(
                ["git", "clone", authenticated_url, temp_dir],
                check=True,
                capture_output=True,
                text=True,
                timeout=60
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=400, detail=f"Failed to clone repository: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=408, detail="Repository clone timeout")

        # Find assignment folder
        assignment_path = os.path.join(temp_dir, request.assignment_name)
        if not os.path.isdir(assignment_path):
            raise HTTPException(status_code=404, detail=f"Assignment folder '{request.assignment_name}' not found in the repository.")

        # Collect all Java files
        source_files = []
        for root, _, files in os.walk(assignment_path):
            for file in files:
                if file.endswith(".java"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        # Store relative path for cleaner output
                        relative_path = os.path.relpath(file_path, assignment_path)
                        source_files.append({"path": relative_path, "content": content})
                    except Exception as e:
                        print(f"Warning: Could not read {file_path}: {e}")

        if not source_files:
            raise HTTPException(status_code=404, detail=f"No Java files found in '{request.assignment_name}'.")

        # Grade the assignment
        grading_result = await _grade_with_gemini_and_regex(
            source_files=source_files,
            natural_language_rubric=assignment.criteria.natural_language_rubric,
            regex_checks=assignment.criteria.regex_checks or [],
            gemini_api_key=request.gemini_api_key
        )

        # Save the grading result to database
        new_grading_result = models.GradingResult(
            assignment_id=assignment.id,
            student_id=student_id,
            grade=grading_result["grade"],
            feedback=grading_result["feedback"]
        )
        db.add(new_grading_result)
        db.commit()

        return {
            "message": "Assignment grading complete.",
            "student_id": student_id,
            "assignment_name": request.assignment_name,
            "grading_result": grading_result
        }


def _extract_student_id(repo_url: str) -> str:
    """Extract student username from GitHub URL"""
    try:
        # Match github.com/username/repo or github.com/username
        match = re.search(r'github\.com[:/]([^/]+)', repo_url)
        if match:
            return match.group(1)
        return "unknown_student"
    except Exception:
        return "unknown_student"


async def _grade_with_gemini_and_regex(
    source_files: list,
    natural_language_rubric: str,
    regex_checks: list,
    gemini_api_key: str
) -> dict:
    """
    Grade using both regex checks and Gemini API analysis.
    Returns: {"grade": int, "feedback": str, "deductions": list}
    """
    deductions = []
    total_deduction = 0

    # Step 1: Apply regex checks for automatic deductions
    for file in source_files:
        file_path = file["path"]
        content = file["content"]
        lines = content.splitlines()

        for check in regex_checks:
            pattern = check.get("pattern")
            deduction = check.get("deduction")
            message = check.get("message")

            if not all([pattern, deduction, message]):
                continue

            for i, line in enumerate(lines, 1):
                try:
                    if re.search(pattern, line):
                        total_deduction += deduction
                        deduction_entry = f"[-{deduction} points] {message} (in {file_path}:{i})"
                        deductions.append(deduction_entry)
                        break  # Only deduct once per file per pattern
                except re.error as e:
                    print(f"Invalid regex pattern '{pattern}': {e}")

    # Step 2: Use Gemini API for design pattern and code quality evaluation
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Prepare code context for Gemini
        code_context = _prepare_code_for_gemini(source_files)

        # Create the grading prompt
        prompt = f"""You are a university teaching assistant grading a Java programming assignment.
Your task is to evaluate the student's code based on the following grading rubric and provide detailed feedback.

GRADING RUBRIC:
{natural_language_rubric}

STUDENT'S CODE:
{code_context}

INSTRUCTIONS:
1. Evaluate the code against the rubric criteria
2. Focus on design patterns, code structure, architecture, and best practices
3. Provide specific deductions with point values (e.g., "-5 points: ...")
4. Each deduction should be on a new line starting with the point deduction
5. Be constructive but thorough
6. Start your response directly with deductions and feedback
7. Format each deduction as: [-X points] Description of issue

Provide your grading feedback now:"""

        # Call Gemini API
        response = model.generate_content(prompt)
        gemini_feedback = response.text.strip()

        # Parse Gemini's response for additional deductions
        gemini_deductions, gemini_deduction_total = _parse_gemini_deductions(gemini_feedback)
        deductions.extend(gemini_deductions)
        total_deduction += gemini_deduction_total

    except Exception as e:
        # If Gemini fails, log and continue with regex-only grading
        print(f"Gemini API error: {e}")
        gemini_feedback = f"[Gemini API Error: {str(e)}] Could not perform AI-assisted grading. Only regex checks were applied."

    # Calculate final grade
    final_grade = max(0, 100 - total_deduction)

    # Format final feedback
    feedback_parts = []
    feedback_parts.append(f"GRADE: {final_grade}/100\n")
    feedback_parts.append("=" * 50)
    feedback_parts.append("\nDEDUCTIONS:")
    if deductions:
        for deduction in deductions:
            feedback_parts.append(f"  {deduction}")
    else:
        feedback_parts.append("  No deductions - Excellent work!")

    feedback_parts.append("\n" + "=" * 50)
    feedback_parts.append("\nDETAILED FEEDBACK:")
    feedback_parts.append(gemini_feedback if 'gemini_feedback' in locals() else "No detailed feedback available.")

    return {
        "grade": final_grade,
        "feedback": "\n".join(feedback_parts),
        "deductions": deductions
    }


def _prepare_code_for_gemini(source_files: list, max_chars: int = 20000) -> str:
    """
    Prepare source code for Gemini API with token limits.
    Concatenates files with clear separators.
    """
    code_parts = []
    total_chars = 0

    for file in source_files:
        file_header = f"\n{'='*60}\nFILE: {file['path']}\n{'='*60}\n"
        file_content = file['content']

        # Check if adding this file would exceed limit
        if total_chars + len(file_header) + len(file_content) > max_chars:
            code_parts.append("\n[... Additional files truncated due to length ...]")
            break

        code_parts.append(file_header)
        code_parts.append(file_content)
        total_chars += len(file_header) + len(file_content)

    return "\n".join(code_parts)


def _parse_gemini_deductions(gemini_response: str) -> tuple[list[str], int]:
    """
    Parse Gemini's response to extract deductions and calculate total.
    Looks for patterns like "[-5 points]" or "-5 points:"
    """
    deductions = []
    total_deduction = 0

    # Regex to match deduction patterns: [-X points] or -X points:
    pattern = r'\[?-\s*(\d+)\s*points?\]?[:\s](.+?)(?=\n|$)'
    matches = re.finditer(pattern, gemini_response, re.IGNORECASE | re.MULTILINE)

    for match in matches:
        points = int(match.group(1))
        description = match.group(2).strip()
        total_deduction += points
        deductions.append(f"[-{points} points] {description}")

    return deductions, total_deduction


async def get_all_grades(db: Session):
    results = db.query(models.GradingResult).options(joinedload(models.GradingResult.assignment)).all()
    response = []
    for result in results:
        response.append(
            GradingResultSchema(
                assignment_name=result.assignment.name,
                student_id=result.student_id,
                grade=result.grade,
                feedback=result.feedback,
            )
        )
    return response


async def get_grades_by_student(student_name: str, db: Session):
    results = db.query(models.GradingResult).filter(
        models.GradingResult.student_id == student_name
    ).options(joinedload(models.GradingResult.assignment)).all()
    response = []
    for result in results:
        response.append(
            GradingResultSchema(
                assignment_name=result.assignment.name,
                student_id=result.student_id,
                grade=result.grade,
                feedback=result.feedback,
            )
        )
    return response
