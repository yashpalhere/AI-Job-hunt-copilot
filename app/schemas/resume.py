from pydantic import BaseModel,ConfigDict
from datetime import datetime

class ResumeResponse(BaseModel):
    id : int 
    raw_text : str
    parsed_skills : list[str] | None
    parsed_experience_summary: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResumeParsed (BaseModel):
    skills : list[str]
    experience_summary: str