from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.schemas.grading import GradingRequest, AssignmentCreate
from app.schemas.grading_result import GradingResult as GradingResultSchema
from app.services import grading_service
from . import deps
from typing import List

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "FastAPI is connected!"}

@router.post("/grade")
async def grade_assignment_endpoint(request: GradingRequest, db: Session = Depends(deps.get_db)):
    return await grading_service.grade_assignment(request, db)

@router.post("/assignments")
async def create_assignment_endpoint(request: AssignmentCreate, db: Session = Depends(deps.get_db)):
    return await grading_service.create_assignment(request, db)

@router.post("/assignments/{assignment_name}/criteria")
async def upload_criteria(
    assignment_name: str, 
    criteria_file: UploadFile = File(...),
    db: Session = Depends(deps.get_db)
):
    return await grading_service.save_criteria(assignment_name, criteria_file, db)

@router.get("/grades", response_model=List[GradingResultSchema])
async def get_grades(db: Session = Depends(deps.get_db)):
    return await grading_service.get_all_grades(db)

@router.get("/grades/{student_name}", response_model=List[GradingResultSchema])
async def get_student_grades(student_name: str, db: Session = Depends(deps.get_db)):
    return await grading_service.get_grades_by_student(student_name, db)
