from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from .database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(200), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="APPLIED")  # APPLIED/INTERVIEW/OFFER/REJECTED
    applied_on = Column(Date, nullable=True)
    notes = Column(String(2000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
