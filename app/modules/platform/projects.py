from __future__ import annotations

import hashlib
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Channel, Project, ProjectStageHead
from app.core.ids import new_id
from app.core.time import utc_now
from app.core.hashing import canonical_json

WORKFLOW_STAGES = [
    ("authoring", "Idea → Script → Shot Plan"),
    ("resolver", "Asset Resolver"),
    ("generation", "G-Labs Image Generation"),
    ("rigging", "Native Auto-Rig"),
    ("director", "AI Animation Director"),
    ("motion", "Motion Planner + Spine Preview"),
    ("delivery", "Shot Render → Voice → MP4"),
]


class ProjectService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, channel_id: str, name: str, description: str) -> Project:
        if self.session.get(Channel, channel_id) is None:
            raise LookupError("channel not found")
        project = Project(project_id=new_id("prj"), channel_id=channel_id, name=name, description=description, status="active", created_at=utc_now(), updated_at=utc_now())
        self.session.add(project)
        self.session.commit()
        return project

    def stages(self, project: Project) -> list[dict]:
        heads = {head.stage_key: head for head in self.session.scalars(select(ProjectStageHead).where(ProjectStageHead.project_id == project.project_id))}
        records = []
        for key, label in WORKFLOW_STAGES:
            head = heads.get(key)
            status = "approved" if head and head.approval_status == "approved" else "stale" if head and head.approval_status == "stale" else "failed" if head and head.approval_status == "rejected" else "draft" if head else "ready" if key == "authoring" and self._has_valid_approved_dna(project.channel_id) else "blocked"
            records.append({"stage_key": key, "label": label, "status": status, "artifact_id": head.artifact_id if head else None, "blocked_reason": None if status != "blocked" else "Prerequisites are not implemented or approved."})
        return records

    def _has_valid_approved_dna(self, channel_id: str) -> bool:
        from app.modules.platform.channels import ChannelDNAValidationError, validate_channel_dna
        channel = self.session.get(Channel, channel_id)
        if channel is None or not channel.dna_json or not channel.dna_json.get("artifact_id"):
            return False
        from app.db.models import Artifact
        artifact_id = channel.dna_json["artifact_id"]
        artifact = self.session.get(Artifact, artifact_id)
        if artifact is None or artifact.kind != "channel_dna" or artifact.status != "ready" or artifact.approved_at is None or artifact.channel_id != channel_id:
            return False
        try:
            payload = Path(artifact.path).read_bytes()
            if f"sha256:{hashlib.sha256(payload).hexdigest()}" != artifact.sha256:
                return False
            if payload != canonical_json(channel.dna_json):
                return False
            validate_channel_dna(channel.dna_json, {"channel_id": channel.channel_id, "name": channel.name, "language": channel.language, "niche": channel.niche, "audience": channel.audience})
            return True
        except (OSError, UnicodeError, ValueError, KeyError, TypeError, ChannelDNAValidationError):
            return False
