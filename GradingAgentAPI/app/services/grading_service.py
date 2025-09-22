from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.schemas.grading import GradingRequest, AssignmentCreate
from app.db import models
from app.schemas.grading_result import GradingResult as GradingResultSchema
import tempfile
import subprocess
import os
import docx

import docx

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
    assignment = db.query(models.Assignment).filter(models.Assignment.name == assignment_name).first()
    if not assignment:
        assignment = models.Assignment(name=assignment_name)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

    file_extension = criteria_file.filename.split('.')[-1]
    if file_extension not in ['txt', 'docx', 'json']:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt, .docx, and .json files are allowed.")

    if file_extension == 'docx':
        try:
            doc = docx.Document(criteria_file.file)
            criteria_text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing .docx file: {e}")
    else:
        criteria_text_bytes = await criteria_file.read()
        criteria_text = criteria_text_bytes.decode("utf-8")

    criteria = db.query(models.Criteria).filter(models.Criteria.assignment_id == assignment.id).first()
    if criteria:
        criteria.text = criteria_text
    else:
        criteria = models.Criteria(assignment_id=assignment.id, text=criteria_text)
        db.add(criteria)
    
    db.commit()
    return {"message": f"Criteria for {assignment_name} saved."}

async def grade_assignment(request: GradingRequest, db: Session) -> dict:
    repo_url = str(request.repo_link)
    authenticated_url = repo_url.replace("https://", f"https://oauth2:{request.token}@")

    assignment = db.query(models.Assignment).filter(models.Assignment.name == request.assignment_name).first()
    if not assignment or not assignment.criteria:
        raise HTTPException(status_code=404, detail=f"Grading criteria for '{request.assignment_name}' not found.")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            subprocess.run(
                ["git", "clone", authenticated_url, temp_dir],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=400, detail=f"Failed to clone repository: {e.stderr}")

        assignment_path = os.path.join(temp_dir, request.assignment_name)

        if not os.path.isdir(assignment_path):
            raise HTTPException(status_code=404, detail=f"Assignment folder '{request.assignment_name}' not found in the repository.")

        source_files = []
        for root, _, files in os.walk(assignment_path):
            for file in files:
                if file.endswith(".java"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    source_files.append({"path": file_path, "content": content})
        
        if not source_files:
            raise HTTPException(status_code=404, detail=f"No Java files found in '{request.assignment_name}'.")

        grading_result = await _grade_with_gemini(source_files, assignment.criteria.text)

        # Save the grading result
        student_id = "student_placeholder" # You would get this from the request or auth
        new_grading_result = models.GradingResult(
            assignment_id=assignment.id,
            student_id=student_id,
            grade=grading_result["grade"],
            feedback=grading_result["feedback"]
        )
        db.add(new_grading_result)
        db.commit()

        return {
            "message": "Assignment analysis complete.",
            "assignment_name": request.assignment_name,
            "grading_result": grading_result
        }

import re
import json

async def _grade_with_gemini(source_files: list, criteria: str) -> dict:
    try:
        grading_criteria = json.loads(criteria)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid criteria format. Criteria must be a valid JSON.")

    grade = 100
    feedback = ""

    for file in source_files:
        file_path = file["path"]
        content = file["content"]
        lines = content.splitlines()

        for criterion in grading_criteria:
            pattern = criterion.get("pattern")
            deduction = criterion.get("deduction")
            message = criterion.get("message")

            if not all([pattern, deduction, message]):
                continue

            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    grade -= deduction
                    feedback += f"- {deduction} points: {message} in {file_path} on line {i}\n"

    return {
        "grade": grade,
        "feedback": feedback.strip()
    }

async def get_all_grades(db: Session):
    results = db.query(models.GradingResult).options(joinedload(models.GradingResult.assignment)).all()
    # We need to manually construct the response to include the assignment name
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
    results = db.query(models.GradingResult).filter(models.GradingResult.student_id == student_name).options(joinedload(models.GradingResult.assignment)).all()
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
