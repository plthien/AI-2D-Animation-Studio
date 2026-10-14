from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.errors import ApiError
from app.db.dependencies import get_db
from app.db.models import Artifact, Project
from app.api.schemas.base import ArtifactResponse, DataEnvelope, ErrorEnvelope, PageResponse

router = APIRouter(prefix="/projects", tags=["artifacts"], responses={404: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}, 500: {"model": ErrorEnvelope}})


@router.get("/{project_id}/artifacts", response_model=DataEnvelope[PageResponse[ArtifactResponse]])
def list_project_artifacts(project_id: str, kind: str | None = None, page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)) -> dict:
    if db.get(Project, project_id) is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", "Project was not found.")
    query = select(Artifact).where(Artifact.project_id == project_id)
    count_query = select(func.count()).select_from(Artifact).where(Artifact.project_id == project_id)
    if kind:
        query, count_query = query.where(Artifact.kind == kind), count_query.where(Artifact.kind == kind)
    safe_size = min(max(page_size, 1), 100)
    artifacts = db.scalars(query.order_by(Artifact.created_at.desc()).offset((max(page, 1) - 1) * safe_size).limit(safe_size))
    items = [{"artifact_id": item.artifact_id, "kind": item.kind, "logical_key": item.logical_key, "version": item.version, "sha256": item.sha256, "size_bytes": item.size_bytes, "status": item.status, "created_at": item.created_at} for item in artifacts]
    return {"data": {"items": items, "total": db.scalar(count_query) or 0, "page": max(page, 1), "page_size": safe_size}}
