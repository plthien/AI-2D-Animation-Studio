from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job


class JobService:
    def __init__(self, session: Session):
        self.session = session

    def list(self, project_id: str | None, offset: int, limit: int) -> list[Job]:
        query = select(Job).order_by(Job.created_at.desc())
        if project_id:
            query = query.where(Job.project_id == project_id)
        return list(self.session.scalars(query.offset(offset).limit(limit)))

    def get(self, job_id: str) -> Job | None:
        return self.session.get(Job, job_id)
