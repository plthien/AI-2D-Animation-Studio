from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.errors import ApiError
from app.api.schemas.base import DataEnvelope, ErrorEnvelope, PageResponse, ProjectCreate, ProjectHeadsResponse, ProjectResponse
from app.db.dependencies import get_db
from app.db.models import Artifact, Channel, Job, Project, ProjectStageHead
from app.modules.platform.projects import ProjectService
from app.repositories.projects import ProjectRepository

router = APIRouter(prefix="/projects", tags=["projects"], responses={404: {"model": ErrorEnvelope}, 409: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}, 500: {"model": ErrorEnvelope}})
def project_dict(project: Project, session: Session | None = None) -> dict:
    result = {"project_id": project.project_id, "channel_id": project.channel_id, "name": project.name, "description": project.description, "status": project.status, "created_at": project.created_at, "updated_at": project.updated_at}
    if session is not None:
        result["stages"] = ProjectService(session).stages(project)
    return result


@router.post("", status_code=201, response_model=DataEnvelope[ProjectResponse], response_model_exclude_none=True)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)) -> dict:
    try:
        project = ProjectService(db).create(body.channel_id, body.name, body.description)
    except LookupError:
        raise ApiError(404, "CHANNEL_NOT_FOUND", "Channel was not found.")
    return {"data": project_dict(project, db)}


@router.get("", response_model=DataEnvelope[PageResponse[ProjectResponse]], response_model_exclude_none=True)
def list_projects(channel_id: str | None = None, page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)) -> dict:
    if channel_id is not None and db.get(Channel, channel_id) is None:
        raise ApiError(404, "CHANNEL_NOT_FOUND", "Channel was not found.")
    safe_size = min(max(page_size, 1), 100)
    items = ProjectRepository(db).list(channel_id, (max(page, 1) - 1) * safe_size, safe_size)
    query = select(func.count()).select_from(Project)
    if channel_id:
        query = query.where(Project.channel_id == channel_id)
    return {"data": {"items": [project_dict(item) for item in items], "total": db.scalar(query) or 0, "page": max(page, 1), "page_size": safe_size}}


@router.get("/{project_id}", response_model=DataEnvelope[ProjectResponse], response_model_exclude_none=True)
def get_project(project_id: str, db: Session = Depends(get_db)) -> dict:
    project = ProjectRepository(db).get(project_id)
    if project is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", "Project was not found.")
    return {"data": project_dict(project, db)}


@router.get("/{project_id}/heads", response_model=DataEnvelope[ProjectHeadsResponse])
def get_project_heads(project_id: str, db: Session = Depends(get_db)) -> dict:
    project = db.get(Project, project_id)
    if project is None:
        raise ApiError(404, "PROJECT_NOT_FOUND", "Project was not found.")
    heads = list(db.scalars(select(ProjectStageHead).where(ProjectStageHead.project_id == project_id)))
    return {"data": {"items": [{"stage_key": head.stage_key, "artifact_id": head.artifact_id, "approval_status": head.approval_status, "updated_at": head.updated_at} for head in heads], "stages": ProjectService(db).stages(project)}}
