from fastapi import APIRouter,HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.models.job import Job
from app.core.security import get_current_user

router = APIRouter(
    prefix="/jobs",
    tags=['Jobs']
)

@router.post("/",response_model= JobResponse)
def createJob(job : JobCreate,current_user = Depends(get_current_user),db: Session = Depends(get_db)):
    new_job = Job(
        user_id = current_user.id,
        company = job.company,
        role = job.role,
        url = job.url,
        jd_text =job.jd_text,
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