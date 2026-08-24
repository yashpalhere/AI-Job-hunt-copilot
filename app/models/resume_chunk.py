from sqlalchemy import Column, ForeignKey, Integer, String,Text,DateTime
from datetime import datetime, timezone
from app.database.database  import Base
from pgvector.sqlalchemy import Vector

class ResumeChunk(Base):
    __tablename__ = "resume_chunks"
    id = Column(Integer, primary_key= True)
    resume_id = Column(Integer, ForeignKey("resumes.id"),nullable=False)
    chunk_text = Column(Text, nullable= False)
    embedding = Column(Vector(3072),nullable= False)
    resume_updated_at = Column(DateTime(timezone=True),nullable=False)
    created_at = Column(DateTime(timezone=True),default = lambda: datetime.now(timezone.utc),nullable=False)