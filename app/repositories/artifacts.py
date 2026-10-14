from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.ids import new_id
from app.core.time import utc_now
from app.db.models import Artifact, Project, ProjectStageHead


class ArtifactConflict(Exception):
    """A compare-and-set publication lost to a newer head."""


class ArtifactRepository:
    def __init__(self, session: Session, artifact_root: Path):
        self.session = session
        self.artifact_root = artifact_root.resolve()

    def list_project(self, project_id: str, kind: str | None = None, offset: int = 0, limit: int = 50) -> list[Artifact]:
        query = select(Artifact).where(Artifact.project_id == project_id).order_by(Artifact.created_at.desc())
        if kind:
            query = query.where(Artifact.kind == kind)
        return list(self.session.scalars(query.offset(offset).limit(limit)))

    def publish(self, project_id: str, stage_key: str, channel_id: str, kind: str, logical_key: str, staged_path: Path, expected_head_id: str | None, parents: list[str] | None = None, metadata: dict | None = None, suffix: str = ".json") -> Artifact:
        if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
            raise ValueError("artifact suffix is invalid")
        if not re.fullmatch(r"prj_[0-9a-f]{32}", project_id):
            raise ValueError("project ID is invalid")
        source = staged_path.resolve(strict=True)
        size = source.stat().st_size
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        artifact_id = new_id("art")
        destination_dir = self.artifact_root / project_id / artifact_id
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"{digest}{suffix}"
        created_file = not destination.exists()
        if created_file:
            temp_path = destination_dir / f".{digest}.{artifact_id}.tmp"
            with source.open("rb") as incoming, temp_path.open("xb") as outgoing:
                shutil.copyfileobj(incoming, outgoing)
                outgoing.flush()
                os.fsync(outgoing.fileno())
            if hashlib.sha256(temp_path.read_bytes()).hexdigest() != digest or temp_path.stat().st_size != size:
                temp_path.unlink(missing_ok=True)
                raise ValueError("staged artifact integrity check failed")
            os.replace(temp_path, destination)
        try:
            connection = self.session.connection()
            if connection.dialect.name == "sqlite":
                connection.exec_driver_sql("BEGIN IMMEDIATE")
            project = self.session.get(Project, project_id)
            if project is None or project.channel_id != channel_id:
                raise LookupError("project not found")
            if kind not in {"channel_dna", "topic_ideas", "script", "shot_plan", "asset_requirements", "asset_resolution", "asset_image", "parts_manifest", "rig_manifest", "rig_profile", "spine_json", "atlas_text", "atlas_png", "animation_plan", "compiled_film", "shot_preview", "rendered_shot", "voice_manifest", "voice_audio", "timing_map", "final_timeline", "final_video", "qc_report"}:
                raise ValueError("artifact kind is unsupported")
            if parents:
                parent_rows = list(self.session.scalars(select(Artifact).where(Artifact.artifact_id.in_(parents))))
                if len(parent_rows) != len(set(parents)) or any(row.channel_id != channel_id or (row.project_id is not None and row.project_id != project_id) for row in parent_rows):
                    raise LookupError("artifact parent not found")
            version = (self.session.scalar(select(func.max(Artifact.version)).where(Artifact.channel_id == channel_id, Artifact.logical_key == logical_key)) or 0) + 1
            artifact = Artifact(artifact_id=artifact_id, project_id=project_id, channel_id=channel_id, kind=kind, logical_key=logical_key, version=version, sha256=f"sha256:{digest}", size_bytes=size, path=str(destination), status="ready", approved_at=None, parents_json=parents or [], metadata_json=metadata or {}, created_at=utc_now())
            current = self.session.scalar(select(ProjectStageHead.artifact_id).where(ProjectStageHead.project_id == project_id, ProjectStageHead.stage_key == stage_key))
            if current != expected_head_id:
                raise ArtifactConflict("stage head changed")
            self.session.add(artifact)
            if current is None:
                self.session.add(ProjectStageHead(project_id=project_id, stage_key=stage_key, artifact_id=artifact_id, approval_status="draft", updated_at=utc_now()))
            else:
                result = self.session.execute(update(ProjectStageHead).where(ProjectStageHead.project_id == project_id, ProjectStageHead.stage_key == stage_key, ProjectStageHead.artifact_id == expected_head_id).values(artifact_id=artifact_id, approval_status="draft", updated_at=utc_now()))
                if result.rowcount != 1:
                    raise ArtifactConflict("stage head changed")
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            if created_file:
                destination.unlink(missing_ok=True)
            raise ArtifactConflict("publication collided with a newer head or version") from error
        except Exception:
            self.session.rollback()
            if created_file:
                destination.unlink(missing_ok=True)
            raise
        return artifact
