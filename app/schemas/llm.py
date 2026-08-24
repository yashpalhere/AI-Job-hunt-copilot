from pydantic import BaseModel


class RAGResponse(BaseModel):
    answer: str

class RAGQuery(BaseModel):
    query: str