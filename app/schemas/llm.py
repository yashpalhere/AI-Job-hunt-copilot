from pydantic import BaseModel,Field    
from typing import Literal
from enum import Enum

class RAGResponse(BaseModel):
    answer: str

class RAGQuery(BaseModel):
    query: str

class DraftedApplication(BaseModel):
    draft: str

class ChatMessage(BaseModel):
    role : Literal['user','assistant']
    content : str


class AgentJobStatus(str, Enum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"

class PendingAction(BaseModel):
    action : Literal['update_job']
    job_id : int    
    new_status: AgentJobStatus

class AgentChatRequest(BaseModel):
    messages : list[ChatMessage]
    pending_action : PendingAction | None = None    

class AgentChatResponse(BaseModel):
    reply: str
    pending_action : PendingAction | None= None

class JobMatch(BaseModel):
    job_id : int
    company  : str
    role : str
    status : AgentJobStatus


class UpdateJobAgentResult(BaseModel):
    message: str
    jobs : list[JobMatch] = Field(default_factory=list)
    pending_action : PendingAction | None= None

class ConfirmationResult(BaseModel):
    decision: Literal["confirm", "reject", "unclear"]
