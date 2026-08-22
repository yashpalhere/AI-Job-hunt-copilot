from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.job import JobMatch
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash")
structured_llm = llm.with_structured_output(JobMatch)

prompt = ChatPromptTemplate.from_messages([
    ("system","""You are a job-resume matching system.Compare the candidate's resume with the job requirements.Calculate a match score from 0 to 100.Identify skills that match.Identify required skills missing from the resume.Provide a concise explanation for the score."""),("human","""Resume Skills:{resume_skills}Resume Experience:{resume_experience}Job Role:{job_role}Required Job Skills:{job_skills}Job Description:{job_description}""")
    ])
chain = prompt | structured_llm

def calculate_job_match (resume_skills : list[str], resume_experience: str | None, job_role : str, job_skills: list[str],job_description: str) -> JobMatch:
    result = chain.invoke({
        "resume_skills": resume_skills,
        "resume_experience": resume_experience or "",
        "job_role": job_role,
        "job_skills": job_skills,
        "job_description": job_description
    })
    return result
