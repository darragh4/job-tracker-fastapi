from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

class JobStatus(str, Enum):
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"

class JobBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    company: str = Field(min_length=1, max_length=200)
    status: JobStatus = JobStatus.APPLIED
    applied_on: Optional[date] = None
    notes: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    status: Optional[JobStatus] = None
    applied_on: Optional[date] = None
    notes: Optional[str] = None

class JobOut(JobBase):
    id: int
    class Config:
        from_attributes = True
