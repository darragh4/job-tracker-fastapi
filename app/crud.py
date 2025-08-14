from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas

def create_job(db: Session, data: schemas.JobCreate):
    job = models.Job(**data.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def list_jobs(
    db: Session,
    status: Optional[schemas.JobStatus] = None,
    company: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    sort: str = "-id",
):
    query = db.query(models.Job)

    if status:
        # status is an Enum; use its value for comparison
        query = query.filter(models.Job.status == status.value)

    if company:
        like = f"%{company}%"
        query = query.filter(models.Job.company.ilike(like))

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Job.title.ilike(like),
                models.Job.company.ilike(like),
                models.Job.notes.ilike(like),
            )
        )

    sort_field = sort.lstrip("-")
    desc = sort.startswith("-")
    col = getattr(models.Job, sort_field, models.Job.id)
    col = col.desc() if desc else col.asc()

    return (
        query.order_by(col)
             .offset(offset)
             .limit(min(max(limit, 1), 100))  # clamp 1..100
             .all()
    )

def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def update_job(db: Session, job_id: int, data: schemas.JobUpdate):
    job = get_job(db, job_id)
    if not job:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(job, k, v)
    db.commit()
    db.refresh(job)
    return job

def delete_job(db: Session, job_id: int):
    job = get_job(db, job_id)
    if not job:
        return False
    db.delete(job)
    db.commit()
    return True
