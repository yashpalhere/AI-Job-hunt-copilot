from fastapi import APIRouter, HTTPException,Depends,UploadFile,File
from app.database.database import get_db
from app.schemas.resume import ResumeResponse
from app.models.resume import Resume
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.services.resume_service import extract_resume_text,parse_resume
router = APIRouter(
    prefix="/resume",
    tags=['Resume']
)

@router.post("/",response_model= ResumeResponse)
def uploadResume(resume : UploadFile = File(...),db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    extracted_raw_text = extract_resume_text(resume)
    parsed_text = parse_resume(extracted_raw_text)
    new_resume = Resume(
        user_id = current_user.id,
        raw_text = extracted_raw_text,
        parsed_skills = parsed_text.skills,
        parsed_experience_summary = parsed_text.experience_summary
    )
    existing_resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not existing_resume:
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        return new_resume
    update_data = {
        "raw_text": extracted_raw_text,
        "parsed_skills": parsed_text.skills,
        "parsed_experience_summary": parsed_text.experience_summary
    }
    for key, value in update_data.items():  
        setattr(existing_resume, key, value)
    db.commit()
    db.refresh(existing_resume)
    return existing_resume