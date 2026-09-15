from langchain_core.tools import tool
from app.services.tools_service import update_job_agent
from app.schemas.llm import AgentJobStatus
from app.services.rag_service import retrieve_relevant_information, generate_rag_answer
from app.services.draft_application_service import draft_tailored_application
from app.models.job import Job
from app.models.resume import Resume
def create_agent_tools (db ,current_user):
    @tool
    def job_query_info(company: str,new_status: AgentJobStatus,selection: int | None = None):
        """
        Find the user's job matching the company and prepare information
        for a possible status update.

        On the first call, omit selection.

        If multiple jobs are returned and the user then selects an option
        number such as 1, 2, or 3, pass that number as selection.

        IMPORTANT:
        selection is the POSITION in the previously displayed list,
        NOT the database job_id.

        Example:
        If the tool previously returned:

        1. Backend Engineer (Job ID: 6)
        2. AI Engineer Intern (Job ID: 1)

        and the user says "1", call this tool with:
        selection=1

        This resolves to Job ID 6.
        """

        result = update_job_agent(
            company=company,
            new_status=new_status,
            selection=selection,
            current_user=current_user,
            db=db
        )

        return result.model_dump()

    @tool
    def rag_job_question(query: str , company: str | None = None, job_id: int | None = None):
        """
        Answer a user's question about their suitability for a specific job
        using relevant resume information and the job's matching data.
        """
        jobs = db.query(Job).filter(Job.user_id == current_user.id,Job.company.ilike(f"%{company}%")).all()

        if job_id:
            job = db.query(Job).filter(
                Job.id == job_id,
                Job.user_id == current_user.id
            ).first()

            if not job:
                return {
                    "message": "Job not found."
                }

        else:
            if not jobs:
                return {
                    "message": "Job not found."
                }

            if len(jobs) > 1:
                return {
                    "message": "I found multiple jobs for this company. Please specify the role.",
                    "jobs": [
                        {
                            "job_id": job.id,
                            "company": job.company,
                            "role": job.role
                        }
                        for job in jobs
                    ]
                }

            job = jobs[0]
        resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
        if not resume:
            return {
                "message": "Resume not found."
            }
        
        retrieved_chunks = retrieve_relevant_information(resume_id=resume.id, query=query, db=db)
        if not retrieved_chunks: 
            return {
                "message": "No relevent resume information was found."
            }
        result = generate_rag_answer(query=query, retrieved_chunks=retrieved_chunks,job=job)
        return result.model_dump()

    @tool
    def draft_application(company: str,job_id: int | None = None):
        """
        Draft a tailored job application for a specific job using
        relevant information from the user's resume and the job description.
        """
        jobs = db.query(Job).filter(Job.user_id ==  current_user.id,Job.company.ilike(f"%{company}%")).all()
        if job_id:
            job = db.query(Job).filter(
                Job.id == job_id,
                Job.user_id == current_user.id
            ).first()

            if not job:
                return {
                    "message": "Job not found."
                }

        else:
            if not jobs:
                return {
                    "message": "Job not found."
                }

            if len(jobs) > 1:
                return {
                    "message": "I found multiple jobs for this company. Please specify the role.",
                    "jobs": [
                        {
                            "job_id": job.id,
                            "company": job.company,
                            "role": job.role
                        }
                        for job in jobs
                    ]
                }

            job = jobs[0]

        resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
        if not resume:
            return {
                "message": "Resume not found."
            }
                
        retrieved_chunks = retrieve_relevant_information(resume_id=resume.id, query=f"{job.role}  {job.jd_text}", db=db)
        if not retrieved_chunks: 
            return {
                "message": "No relevent resume information was found."
            }
        result = draft_tailored_application(job=job,retrieved_chunks=retrieved_chunks)
        return result.model_dump()
    return [job_query_info,rag_job_question,draft_application]

