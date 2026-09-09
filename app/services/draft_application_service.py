from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.models.resume_chunk import ResumeChunk
from app.schemas.llm import DraftedApplication
from app.models.job import Job
from dotenv import load_dotenv
load_dotenv()
from app.services.rag_service import retrieve_relevant_information
from app.core.config import GEMINI_MODEL

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)
struc_llm = llm.with_structured_output(DraftedApplication)
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an AI job application assistant.

        Your task is to write a tailored application message for the
        candidate based on the provided resume evidence and job information.

        Rules:
        - Use only the information provided in the resume context and job data.
        - Do not invent skills, experience, projects, achievements,
        qualifications, or responsibilities.
        - Highlight the candidate's experience and skills that are relevant
        to the specific job.
        - Do not claim that the candidate has any skill listed as a missing skill.
        - Do not simply repeat the job description. Connect the candidate's
        actual experience to the requirements of the role.
        - Keep the application professional, specific, and concise.
        - Avoid generic filler such as "I am the perfect candidate" or
        unsupported claims about the candidate.
        - The application should sound natural and be suitable for sending
        to a recruiter or hiring manager.
        """
    ),
    ('human', "Resume Context:  \n {resume_context} \n\n Company: \n {company} \n role: \n {role} \n Job Description {jd_text} \n Missing skills: \n {missing_skills} \n Matched Skills: \n {matched_skills} \n Write a tailored application for this position."
    )
])
chain = prompt | struc_llm
def draft_tailored_application(job: Job,retrieved_chunks: list[ResumeChunk]) -> DraftedApplication:
    resume_context = "\n\n".join(chunk.chunk_text for chunk in retrieved_chunks)   
    application = chain.invoke({
            'resume_context': resume_context,
            "company": job.company,
            "role" : job.role,
            "jd_text" : job.jd_text,
            "missing_skills" : job.missing_skills,
            "matched_skills" : job.matched_skills,
        })
    return application
