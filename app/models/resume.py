from sqlalchemy import Column, String, Integer, ForeignKey,Text,DateTime,JSON
from datetime import datetime, timezone
from app.database.database import Base

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False, unique=True)
    raw_text = Column(Text,nullable=False)
    parsed_skills = Column(JSON)
    parsed_experience_summary = Column(Text)
    created_at = Column(DateTime(timezone=True),default= lambda : datetime.now(timezone.utc),nullable=False)
    updated_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc),nullable=False)