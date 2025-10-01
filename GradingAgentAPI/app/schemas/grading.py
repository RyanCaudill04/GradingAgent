from pydantic import BaseModel, HttpUrl
from typing import Optional

class GradingRequest(BaseModel):
    assignment_name: str
    repo_link: HttpUrl
    token: str
    gemini_api_key: str  # TA provides their own key

class AssignmentCreate(BaseModel):
    assignment_name: str

class RegexCheck(BaseModel):
    pattern: str
    deduction: int
    message: str

class CriteriaUpload(BaseModel):
    natural_language_rubric: str
    regex_checks: Optional[list[RegexCheck]] = []
