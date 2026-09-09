from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import get_current_user

from app.services.agent_service import create_job_agent
from app.schemas.llm import AgentChatRequest , AgentChatResponse

from app.services.tools_service import  handle_pending_action

from langchain_core.messages import ToolMessage,AIMessage
import json

router = APIRouter(
    prefix="/agent",
    tags=['Agent']
)

@router.post("/chat",response_model= AgentChatResponse)
def agent_chat(request : AgentChatRequest, db : Session = Depends(get_db),current_user = Depends(get_current_user)):
    if request.pending_action:
        pending_action_response= handle_pending_action(pending_action= request.pending_action,user_message=request.messages[-1].content,current_user= current_user, db=db)
        return pending_action_response
    else: 
        agent = create_job_agent(current_user= current_user, db=db)
        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": message.role,
                        "content": message.content
                    }
                    for message in request.messages
                ]
            }
        )
        pending_action = None
        ai_message = None
        for message in response["messages"]:
            if isinstance(message, ToolMessage):
                tool_result = json.loads(message.content)
                tool_name = message.name
                if tool_name == "job_query_info":
                    pending_action = tool_result["pending_action"]
            if isinstance(message, AIMessage) and message.content:
                if isinstance(message.content, str):
                    ai_message = message.content
                else:
                    ai_message = "".join( part['text'] for part in message.content if isinstance(part,dict) and part.get("type") == "text")
        response = AgentChatResponse(
            reply= ai_message,
            pending_action= pending_action
        )
        return response