from pydantic import BaseModel, EmailStr, Field,Json,ConfigDict
from app.models.job import JobStatus
from datetime import date,datetime
class JobCreate(BaseModel):
    company : str
    role : str
    url : str 
    jd_text : str 
    status : JobStatus
    notes :str 

class JobUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    url: str | None = None
    jd_text: str | None = None
    status: JobStatus | None = None
    applied_date: date | None = None
    notes: str | None = None

class JobResponse(BaseModel):
    id : int
    company: str 
    role: str 
    url: str 
    jd_text: str 
    parsed_skills : list[str] | None 
    match_score : float | None
    status : JobStatus
    applied_date : date | None
    notes : str | None
    created_at : datetime
    updated_at : datetime
    model_config = ConfigDict(from_attributes = True)

class JobParsed(BaseModel):
    required_skills: list[str]

class JobMatch(BaseModel):
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str