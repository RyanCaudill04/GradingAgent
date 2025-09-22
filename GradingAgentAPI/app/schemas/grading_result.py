from pydantic import BaseModel

class GradingResult(BaseModel):
    assignment_name: str
    student_id: str
    grade: float
    feedback: str

    class Config:
        from_attributes = True
