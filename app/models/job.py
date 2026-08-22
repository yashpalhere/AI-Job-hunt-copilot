from sqlalchemy import Column, Integer, String,ForeignKey,Text,JSON,Float,DateTime,Date
from sqlalchemy import Enum as SqlEnum
from app.database.database import Base
from enum import Enum as PyEnum
from datetime import datetime , timezone
class JobStatus ( PyEnum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"

class Job ( Base):
    __tablename__ = "jobs"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    company = Column (String, nullable= False,)
    role = Column (String, nullable=False)
    url = Column(String, nullable= False)
    jd_text =Column(Text, nullable= False)
    parsed_skills = Column(JSON)
    status = Column(
        SqlEnum(
            JobStatus,
            values_callable=lambda enum_class: [member.value for member in enum_class]
        ),
        nullable=False
    ) 
    match_score = Column( Float )
    applied_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),nullable= False)
    updated_at = Column(DateTime(timezone=True),default= lambda: datetime.now(timezone.utc) , onupdate=lambda: datetime.now(timezone.utc),nullable=False)