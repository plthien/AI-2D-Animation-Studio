from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PageQuery(StrictModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


class ChannelCreate(StrictModel):
    name: str = Field(min_length=1, max_length=200)
    language: str = Field(min_length=1, max_length=32)
    niche: str = Field(min_length=1, max_length=200)
    audience: str = Field(min_length=1, max_length=200)


class ProjectCreate(StrictModel):
    channel_id: str = Field(pattern=r"^chn_[0-9a-f]{32}$")
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)


T = TypeVar("T")


class DataEnvelope(StrictModel, Generic[T]):
    data: T


class PageResponse(StrictModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ChannelResponse(StrictModel):
    channel_id: str
    name: str
    language: str
    niche: str
    audience: str
    created_at: str
    updated_at: str


class ChannelDNAResponse(StrictModel):
    dna: dict | None
    artifact_id: str | None
    visual_style_hash: str | None
    performance_style_hash: str | None
    narration_identity_hash: str | None


class StageResponse(StrictModel):
    stage_key: str
    label: str
    status: str
    artifact_id: str | None
    blocked_reason: str | None


class ProjectResponse(StrictModel):
    project_id: str
    channel_id: str
    name: str
    description: str
    status: str
    created_at: str
    updated_at: str
    stages: list[StageResponse] | None = None


class StageHeadResponse(StrictModel):
    stage_key: str
    artifact_id: str
    approval_status: str
    updated_at: str


class ProjectHeadsResponse(StrictModel):
    items: list[StageHeadResponse]
    stages: list[StageResponse]


class ArtifactResponse(StrictModel):
    artifact_id: str
    kind: str
    logical_key: str
    version: int
    sha256: str
    size_bytes: int
    status: str
    created_at: str


class JobResponse(StrictModel):
    job_id: str
    operation_id: str | None
    project_id: str
    kind: str
    status: str
    progress: int
    heartbeat_at: str | None
    created_at: str
    updated_at: str


class ErrorBody(StrictModel):
    code: str
    message: str
    retryable: bool
    details: dict


class ErrorEnvelope(StrictModel):
    error: ErrorBody


class HealthResponse(StrictModel):
    status: str
    schema_version: str
