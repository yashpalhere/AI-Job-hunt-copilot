from fastapi import APIRouter,HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse   
from app.models.job import Job
from app.core.security import get_current_user
from app.services.job_service import parse_job
from app.services.matching_service import calculate_job_match
from app.models.resume import Resume
from app.schemas.job import JobMatch
from datetime import datetime,timezone
router = APIRouter(
    prefix="/jobs",
    tags=['Jobs']
)

@router.post("/",response_model= JobResponse)
def createJob(job : JobCreate,current_user = Depends(get_current_user),db: Session = Depends(get_db)):
    parsed_job = parse_job(company=job.company,role=job.role,jd_text=job.jd_text)
    new_job = Job(
        user_id = current_user.id,
        company = job.company,
        role = job.role,
        url = job.url,
        jd_text =job.jd_text,
        parsed_skills=parsed_job.required_skills,
        status =job.status,
        notes =job.notes
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("/",response_model=list[JobResponse])
def getJobs (current_user = Depends(get_current_user),db : Session= Depends(get_db)):
    all_jobs = db.query(Job).filter(Job.user_id == current_user.id).all()
    return all_jobs

@router.get("/{job_id}", response_model=JobResponse)
def getJobWithID( job_id:int,current_user = Depends(get_current_user),db: Session = Depends(get_db)):
    user_job = db.query(Job).filter(Job.id == job_id , Job.user_id == current_user.id).first() 
    if not user_job: 
        raise HTTPException(status_code=404, detail="Job not found")
    return user_job


@router.patch("/{job_id}",response_model= JobResponse)
def updatejob(job_id :int,job_data: JobUpdate,current_user = Depends(get_current_user),db: Session = Depends(get_db)):
    user_job = db.query(Job).filter(Job.id == job_id,Job.user_id == current_user.id).first()
    if not user_job:
        raise HTTPException(status_code=404, detail="Job not found")
    update_info = job_data.model_dump(exclude_unset=True)
    for key,value in update_info.items():
        setattr(user_job,key,value)
    db.commit()
    db.refresh(user_job)
    return user_job

@router.delete("/{job_id}")
def deleteJob(job_id = int, current_user = Depends(get_current_user),db: Session = Depends(get_db)):
    user_job = db.query(Job).filter(Job.id == job_id,Job.user_id == current_user.id).first()
    if not user_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(user_job)
    db.commit()
    return {"message": " Job deleted successfully.","Job ID" : job_id}

@router.post("/{job_id}/match",response_model= JobMatch)
def match_job(job_id : int, current_user = Depends(get_current_user),db:Session= Depends(get_db)):


    user_job = db.query(Job).filter(Job.id == job_id,Job.user_id == current_user.id).first()
    if not user_job:
        raise HTTPException(status_code=404, detail="Job not found")
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found. Upload a resume first. ")

    if (user_job.match_computed_at is not None and user_job.match_computed_at >= resume.updated_at):
        return JobMatch(
            match_score=user_job.match_score,
            matched_skills=user_job.matched_skills,
            missing_skills=user_job.missing_skills,
            explanation=user_job.match_explanation
        )
    job_match = calculate_job_match(resume.parsed_skills or [],resume.parsed_experience_summary,user_job.role,user_job.parsed_skills or [],user_job.jd_text)

    user_job.match_score = job_match.match_score
    user_job.matched_skills = job_match.matched_skills
    user_job.missing_skills = job_match.missing_skills
    user_job.match_explanation = job_match.explanation
    user_job.match_computed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user_job)

    return job_match