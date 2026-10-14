from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Project


class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, project_id: str) -> Project | None:
        return self.session.get(Project, project_id)

    def list(self, channel_id: str | None, offset: int, limit: int) -> list[Project]:
        query = select(Project).order_by(Project.created_at.desc(), Project.project_id)
        if channel_id:
            query = query.where(Project.channel_id == channel_id)
        return list(self.session.scalars(query.offset(offset).limit(limit)))
