from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api.errors import ApiError
from app.db.dependencies import get_db
from app.db.models import Job, Project
from app.api.schemas.base import DataEnvelope, ErrorEnvelope, JobResponse, PageResponse
from app.services.jobs import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"], responses={404: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}, 500: {"model": ErrorEnvelope}})


def job_dict(job: Job) -> dict:
    return {"job_id": job.job_id, "operation_id": job.operation_id, "project_id": job.project_id, "kind": job.kind, "status": job.status, "progress": job.progress, "heartbeat_at": job.heartbeat_at, "created_at": job.created_at, "updated_at": job.updated_at}


@router.get("", response_model=DataEnvelope[PageResponse[JobResponse]])
def list_jobs(project_id: str | None = None, page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)) -> dict:
    if project_id is not None and db.get(Project, project_id) is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", "Project was not found.")
    size = min(max(page_size, 1), 100)
    items = JobService(db).list(project_id, (max(page, 1) - 1) * size, size)
    count = select(func.count()).select_from(Job)
    if project_id:
        count = count.where(Job.project_id == project_id)
    return {"data": {"items": [job_dict(item) for item in items], "total": db.scalar(count) or 0, "page": max(page, 1), "page_size": size}}


@router.get("/{job_id}", response_model=DataEnvelope[JobResponse])
def get_job(job_id: str, db: Session = Depends(get_db)) -> dict:
    job = db.get(Job, job_id)
    if job is None:
        raise ApiError(404, "JOB_NOT_FOUND", "Job was not found.")
    return {"data": job_dict(job)}
