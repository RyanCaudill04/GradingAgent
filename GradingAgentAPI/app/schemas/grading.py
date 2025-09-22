from pydantic import BaseModel, HttpUrl

class GradingRequest(BaseModel):
    assignment_name: str
    repo_link: HttpUrl
    token: str

class AssignmentCreate(BaseModel):
    assignment_name: str
