from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.llm import PendingAction,UpdateJobAgentResult,JobMatch,AgentJobStatus,ConfirmationResult
from app.schemas.job import JobUpdate
from app.services.job_service import update_job
from app.models.job import JobStatus
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
from app.database.database import session_local
from app.services.rag_service import retrieve_relevant_information
from app.core.config import GEMINI_MODEL

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)
struc_llm = llm.with_structured_output(ConfirmationResult)

def update_job_agent(company: str,new_status: AgentJobStatus,current_user,db: Session,selection: int | None = None) -> UpdateJobAgentResult:

    all_jobs = (
        db.query(Job)
        .filter(
            Job.user_id == current_user.id,
            Job.company.ilike(f"%{company}%")
        )
        .all()
    )

    if len(all_jobs) == 0:
        return UpdateJobAgentResult(
            message=f"No job matching '{company}' was found."
        )

    # If the user selected an option from the previously displayed list
    if selection is not None:

        if selection < 1 or selection > len(all_jobs):
            return UpdateJobAgentResult(
                message=(
                    f"Invalid selection. Please choose a number from "
                    f"1 to {len(all_jobs)}."
                ),
                jobs=[
                    JobMatch(
                        job_id=job.id,
                        company=job.company,
                        role=job.role,
                        status=AgentJobStatus(job.status.value)
                    )
                    for job in all_jobs
                ]
            )

        # Convert option number -> actual job
        job = all_jobs[selection - 1]

        pending_action = PendingAction(
            action="update_job",
            job_id=job.id,
            new_status=new_status
        )

        job_match = JobMatch(
            job_id=job.id,
            company=job.company,
            role=job.role,
            status=AgentJobStatus(job.status.value)
        )

        return UpdateJobAgentResult(
            message=(
                f"You selected {job.company} — {job.role} "
                f"(Job ID: {job.id}). "
                f"Current status is {job.status.value}. "
                f"Should I change it to {new_status.value}?"
            ),
            jobs=[job_match],
            pending_action=pending_action
        )

    # Exactly one matching job
    if len(all_jobs) == 1:

        job = all_jobs[0]

        pending_action = PendingAction(
            action="update_job",
            job_id=job.id,
            new_status=new_status
        )

        job_match = JobMatch(
            job_id=job.id,
            company=job.company,
            role=job.role,
            status=AgentJobStatus(job.status.value)
        )

        return UpdateJobAgentResult(
            message=(
                f"I found one matching job: {job.company} — {job.role}. "
                f"Current status is {job.status.value}. "
                f"Should I change it to {new_status.value}?"
            ),
            jobs=[job_match],
            pending_action=pending_action
        )

    # Multiple matching jobs
    job_matches = []

    for job in all_jobs:
        job_match = JobMatch(
            job_id=job.id,
            company=job.company,
            role=job.role,
            status=AgentJobStatus(job.status.value)
        )
        job_matches.append(job_match)

    return UpdateJobAgentResult(
        message=(
            f"I found {len(all_jobs)} jobs matching '{company}'. "
            "Please select one by its option number."
        ),
        jobs=job_matches
    )
def confirm_job_update(pending_action: PendingAction,current_user,db: Session):
    job_data = JobUpdate(
        status=JobStatus(pending_action.new_status.value)
)
    updated_job = update_job(
        job_id=pending_action.job_id,
        job_data=job_data,
        current_user=current_user,
        db=db
    )

    if not updated_job:
        return None

    return updated_job
promt = ChatPromptTemplate.from_messages([
    (
        'system',""" 
                You are a confirmation decision classifier for an AI job-management assistant.

                Your task is to determine whether the user's latest message confirms, rejects, or is unclear about a pending action that the assistant previously asked the user to confirm.

                Classify the message into exactly one of these categories:

                - "confirm": The user clearly agrees to or authorizes the pending action.
                Examples include "yes", "yeah", "yup", "okay", "ok", "sure", "go ahead", "do it", "that's fine", or similar expressions of agreement.

                - "reject": The user clearly declines, cancels, or refuses the pending action.
                Examples include "no", "nope", "don't do it", "cancel", "leave it", "never mind", or similar expressions of rejection.

                - "unclear": The user's message does not clearly confirm or reject the pending action, or it introduces a different request that cannot safely be interpreted as confirmation or rejection.

                Rules:
                - Do not guess the user's intention.
                - Be conservative when the meaning is ambiguous.
                - Treat informal expressions such as "yup", "k", "yeah", and "okay" as confirmation when they clearly function as agreement.
                - A new or different instruction is not automatically a confirmation.
                - Return "unclear" whenever you cannot confidently determine that the user confirmed or rejected the pending action.
                - Output only the structured classification requested by the schema.
                """
    ),
    (
        "human","User Message: {user_message}"
    )
    ])
chain = promt | struc_llm
def interpret_decision(human_message: str):
    decision = chain.invoke({'user_message': human_message})
    return decision



def handle_pending_action(pending_action: PendingAction,user_message: str,current_user,db: Session):
    decision = interpret_decision(user_message)

    if decision.decision == "confirm":

        updated_job = confirm_job_update(
            pending_action=pending_action,
            current_user=current_user,
            db=db
        )

        if not updated_job:
            return {
                "reply": "I couldn't find that job.",
                "pending_action": None
            }

        return {
            "reply": (
                f"Updated {updated_job.company} — "
                f"{updated_job.role} to "
                f"{updated_job.status.value}."
            ),
            "pending_action": None
        }

    elif decision.decision == "reject":
        return {
            "reply": "Okay, I didn't make the change.",
            "pending_action": None
        }

    else:
        return {
            "reply": (
                "I wasn't sure whether you wanted me to "
                "confirm or cancel that change."
            ),
            "pending_action": pending_action
        }


