from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time import utc_now
from app.db.base import Base
from app.db.types import JSONText


class Channel(Base):
    __tablename__ = "channels"
    channel_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    niche: Mapped[str] = mapped_column(String(200), nullable=False)
    audience: Mapped[str] = mapped_column(String(200), nullable=False)
    dna_json: Mapped[dict | None] = mapped_column(JSONText, nullable=True)
    voice_profile_json: Mapped[dict | None] = mapped_column(JSONText, nullable=True)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now, onupdate=utc_now, nullable=False)
    visual_style_hash: Mapped[str | None] = mapped_column(String(71), nullable=True)
    performance_style_hash: Mapped[str | None] = mapped_column(String(71), nullable=True)
    narration_identity_hash: Mapped[str | None] = mapped_column(String(71), nullable=True)


class Project(Base):
    __tablename__ = "projects"
    project_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.channel_id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now, onupdate=utc_now, nullable=False)


class Artifact(Base):
    __tablename__ = "artifacts"
    __table_args__ = (UniqueConstraint("channel_id", "logical_key", "version"), Index("ix_artifacts_project_kind", "project_id", "kind"))
    artifact_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.project_id", ondelete="RESTRICT"), nullable=True, index=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.channel_id", ondelete="RESTRICT"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    logical_key: Mapped[str] = mapped_column(String(300), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(71), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    approved_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    parents_json: Mapped[list] = mapped_column(JSONText, default=list, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONText, default=dict, nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)


class ProjectStageHead(Base):
    __tablename__ = "project_stage_heads"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True)
    stage_key: Mapped[str] = mapped_column(String(32), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.artifact_id", ondelete="RESTRICT"), nullable=False)
    approval_status: Mapped[str] = mapped_column(String(24), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)


class AuthoringReservation(Base):
    __tablename__ = "authoring_reservations"
    reservation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    stage_key: Mapped[str] = mapped_column(String(32), nullable=False)
    artifact_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    source_hash: Mapped[str] = mapped_column(String(71), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)
    consumed_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("channel_id", "kind", "semantic_key"), CheckConstraint("kind IN ('character','background','prop')"))
    asset_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.channel_id", ondelete="RESTRICT"), nullable=False)
    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    semantic_key: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)


class AssetVersion(Base):
    __tablename__ = "asset_versions"
    __table_args__ = (UniqueConstraint("asset_id", "version"),)
    asset_version_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.asset_id", ondelete="RESTRICT"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    view: Mapped[str] = mapped_column(String(32), nullable=False)
    style_hash: Mapped[str] = mapped_column(String(71), nullable=False)
    image_artifact_id: Mapped[str | None] = mapped_column(ForeignKey("artifacts.artifact_id"), nullable=True)
    rig_version_id: Mapped[str | None] = mapped_column(ForeignKey("rig_versions.rig_version_id", ondelete="RESTRICT"), nullable=True)
    capabilities_json: Mapped[dict] = mapped_column(JSONText, default=dict, nullable=False)
    source_hashes_json: Mapped[dict] = mapped_column(JSONText, default=dict, nullable=False)
    approved_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class ProjectAssetBinding(Base):
    __tablename__ = "project_asset_bindings"
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True)
    requirement_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    asset_version_id: Mapped[str] = mapped_column(ForeignKey("asset_versions.asset_version_id", ondelete="RESTRICT"), nullable=False)
    rig_version_id: Mapped[str | None] = mapped_column(ForeignKey("rig_versions.rig_version_id", ondelete="RESTRICT"), nullable=True)
    approved_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class Rig(Base):
    __tablename__ = "rigs"
    rig_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.asset_id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)


class RigVersion(Base):
    __tablename__ = "rig_versions"
    __table_args__ = (UniqueConstraint("rig_id", "version"),)
    rig_version_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    rig_id: Mapped[str] = mapped_column(ForeignKey("rigs.rig_id", ondelete="RESTRICT"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    manifest_artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.artifact_id"), nullable=False)
    profile_artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.artifact_id"), nullable=False)
    spine_json_artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.artifact_id"), nullable=False)
    atlas_artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.artifact_id"), nullable=False)
    atlas_png_artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.artifact_id"), nullable=False)
    approved_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class MotionTemplate(Base):
    __tablename__ = "motion_templates"
    __table_args__ = (UniqueConstraint("name", "version"),)
    motion_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    action_kind: Mapped[str] = mapped_column(String(40), nullable=False)
    template_json: Mapped[dict] = mapped_column(JSONText, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)


class Operation(Base):
    __tablename__ = "operations"
    __table_args__ = (UniqueConstraint("project_id", "kind", "idempotency_key"),)
    operation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    input_hash: Mapped[str] = mapped_column(String(71), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    next_reconcile_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    lease_owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lease_token: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lease_expires_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now, onupdate=utc_now, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_details_json: Mapped[dict | None] = mapped_column(JSONText, nullable=True)


class OperationTask(Base):
    __tablename__ = "operation_tasks"
    __table_args__ = (UniqueConstraint("operation_id", "unit_key"),)
    task_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    operation_id: Mapped[str] = mapped_column(ForeignKey("operations.operation_id", ondelete="CASCADE"), nullable=False)
    unit_key: Mapped[str] = mapped_column(String(128), nullable=False)
    provider_task_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    submit_intent_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    last_polled_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    result_artifact_id: Mapped[str | None] = mapped_column(ForeignKey("artifacts.artifact_id"), nullable=True)
    error_json: Mapped[dict | None] = mapped_column(JSONText, nullable=True)


class Job(Base):
    __tablename__ = "jobs"
    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    operation_id: Mapped[str | None] = mapped_column(ForeignKey("operations.operation_id"), nullable=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    heartbeat_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now, nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), default=utc_now, onupdate=utc_now, nullable=False)


Index("uq_authoring_pending_stage", AuthoringReservation.project_id, AuthoringReservation.stage_key, unique=True, sqlite_where=(AuthoringReservation.status == "pending"))
