from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import Artifact
from app.repositories.artifacts import ArtifactRepository


class ArtifactService:
    """Publish immutable project artifacts through the repository CAS boundary."""

    def __init__(self, session: Session, artifact_root: Path):
        self.repository = ArtifactRepository(session, artifact_root)

    def publish(self, *, project_id: str, stage_key: str, channel_id: str, kind: str, logical_key: str, staged_path: Path, expected_head_id: str | None, parents: list[str] | None = None, metadata: dict | None = None, suffix: str = ".json") -> Artifact:
        return self.repository.publish(project_id, stage_key, channel_id, kind, logical_key, staged_path, expected_head_id, parents, metadata, suffix)
