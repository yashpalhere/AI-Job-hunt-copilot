from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.job import JobParsed
from app.models.job import Job
from app.schemas.job import JobUpdate
from sqlalchemy.orm import Session
load_dotenv()
from app.core.config import GEMINI_MODEL

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)
structured_llm = llm.with_structured_output(JobParsed)
prompt = ChatPromptTemplate.from_messages([
    ("system","""You are a job description parser.
            Extract the company name, job role, and required technical
            and professional skills from the provided job description."""
    ),("human","Company: {company} \n Role: {role} \n Job Description:\n{jd_text}")
])
chain = prompt | structured_llm
def parse_job (  company: str, role: str,jd_text : str) -> JobParsed:
    result = chain.invoke ( { "company": company,"role": role,"jd_text": jd_text})
    return result 

def update_job(job_id: int,job_data: JobUpdate,current_user,db: Session):
    user_job = (db.query(Job).filter(Job.id == job_id,Job.user_id == current_user.id).first())

    if not user_job:
        return None

    update_info = job_data.model_dump(exclude_unset=True)

    for key, value in update_info.items():
        setattr(user_job, key, value)

    db.commit()
    db.refresh(user_job)

    return user_job