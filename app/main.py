from fastapi import FastAPI, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import Base, engine, get_db

app = FastAPI(title="Job Tracker API")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/jobs", response_model=schemas.JobOut, status_code=status.HTTP_201_CREATED)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    return crud.create_job(db, job)

@app.get("/jobs", response_model=List[schemas.JobOut])
def list_jobs(
    status: Optional[schemas.JobStatus] = Query(None, description="Filter by status"),
    company: Optional[str] = Query(None, min_length=1, max_length=200, description="Filter by company (contains)"),
    q: Optional[str] = Query(None, description="Free-text search in title/company/notes"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("-id", pattern="^-?(id|applied_on|company|title)$"),
    db: Session = Depends(get_db),
):
    return crud.list_jobs(db, status=status, company=company, q=q, limit=limit, offset=offset, sort=sort)

@app.get("/jobs/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.put("/jobs/{job_id}", response_model=schemas.JobOut)
def update_job(job_id: int, patch: schemas.JobUpdate, db: Session = Depends(get_db)):
    job = crud.update_job(db, job_id, patch)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_job(db, job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return None
