from __future__ import annotations

import hashlib
import os
import re
import shutil
import time
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import func, select, update
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.ids import new_id
from app.core.time import utc_now
from app.db.models import Artifact, Project, ProjectStageHead


ID_PATTERNS = {
    "project": re.compile(r"prj_[0-9a-f]{32}"),
    "channel": re.compile(r"chn_[0-9a-f]{32}"),
    "artifact": re.compile(r"art_[0-9a-f]{32}"),
}
STAGE_KINDS = {
    "authoring": {"topic_ideas", "script", "shot_plan"},
    "resolver": {"asset_requirements", "asset_resolution"},
    "generation": {"asset_image"},
    "rigging": {"parts_manifest", "rig_manifest", "rig_profile", "spine_json", "atlas_text", "atlas_png"},
    "director": {"animation_plan"},
    "motion": {"compiled_film", "shot_preview"},
    "delivery": {"rendered_shot", "voice_manifest", "voice_audio", "timing_map", "final_timeline", "final_video", "qc_report"},
    "topic": {"topic_ideas"},
    "script": {"script"},
    "shot_plan": {"shot_plan"},
    "animation_plan": {"animation_plan"},
    "compiled_film": {"compiled_film"},
    "voice": {"voice_manifest", "voice_audio"},
    "final_video": {"final_video", "qc_report"},
}


class ArtifactConflict(Exception):
    """A compare-and-set publication lost to a newer head."""


class ArtifactPublicationCommitted(RuntimeError):
    """Publication committed, but the caller lost its response after commit."""

    def __init__(self, artifact_id: str):
        super().__init__(f"artifact publication committed as {artifact_id}; reconcile before retrying")
        self.artifact_id = artifact_id


class ArtifactRepository:
    """Immutable publication with an isolated SQLite transaction owner.

    Bytes are copied, hashed and atomically finalized before the owned database
    transaction commits. A crash before the commit can leave only an unreferenced
    artifact-ID directory; a committed head therefore never points at missing
    bytes. ``reconcile_orphans`` removes only old, unreferenced artifact-ID
    directories and never files referenced by artifact metadata.
    """

    def __init__(
        self,
        session: Session,
        artifact_root: Path,
        fault_injector: Callable[[str], None] | None = None,
    ):
        self.session = session
        self.artifact_root = artifact_root.resolve()
        self.artifact_root.mkdir(parents=True, exist_ok=True)
        self.fault_injector = fault_injector

    def list_project(self, project_id: str, kind: str | None = None, offset: int = 0, limit: int = 50) -> list[Artifact]:
        query = select(Artifact).where(Artifact.project_id == project_id).order_by(Artifact.created_at.desc())
        if kind:
            query = query.where(Artifact.kind == kind)
        return list(self.session.scalars(query.offset(offset).limit(limit)))

    def publish(
        self,
        project_id: str,
        stage_key: str,
        channel_id: str,
        kind: str,
        logical_key: str,
        staged_path: Path,
        expected_head_id: str | None,
        parents: list[str] | None = None,
        metadata: dict | None = None,
        suffix: str = ".json",
    ) -> Artifact:
        parent_ids = list(parents or [])
        self._validate_request(project_id, stage_key, channel_id, kind, logical_key, staged_path, expected_head_id, parent_ids, suffix)
        artifact_id = new_id("art")
        staging_path: Path | None = None
        destination: Path | None = None
        destination_dir: Path | None = None
        database_committed = False
        artifact: Artifact | None = None

        try:
            staging_path, digest, size = self._stage_source(staged_path, artifact_id)
            self._fault("after_staging")
            destination_dir = (self.artifact_root / project_id / artifact_id).resolve()
            if not destination_dir.is_relative_to(self.artifact_root):
                raise ValueError("artifact destination escapes storage root")
            destination_dir.mkdir(parents=True, exist_ok=False)
            destination = destination_dir / f"{digest}{suffix}"
            self._fault("before_finalize")
            os.replace(staging_path, destination)
            staging_path = None
            self._fault("after_finalize")

            engine = self._publication_engine()
            with engine.connect() as connection:
                connection.exec_driver_sql("BEGIN IMMEDIATE")
                owned_session = Session(bind=connection, expire_on_commit=False, autoflush=False)
                try:
                    project = owned_session.get(Project, project_id)
                    if project is None or project.channel_id != channel_id:
                        raise LookupError("project not found")
                    self._validate_parents(owned_session, project_id, channel_id, parent_ids)
                    current = owned_session.scalar(
                        select(ProjectStageHead.artifact_id).where(
                            ProjectStageHead.project_id == project_id,
                            ProjectStageHead.stage_key == stage_key,
                        )
                    )
                    if current != expected_head_id:
                        raise ArtifactConflict("stage head changed")
                    version = (
                        owned_session.scalar(
                            select(func.max(Artifact.version)).where(
                                Artifact.channel_id == channel_id,
                                Artifact.logical_key == logical_key,
                            )
                        )
                        or 0
                    ) + 1
                    artifact = Artifact(
                        artifact_id=artifact_id,
                        project_id=project_id,
                        channel_id=channel_id,
                        kind=kind,
                        logical_key=logical_key,
                        version=version,
                        sha256=f"sha256:{digest}",
                        size_bytes=size,
                        path=str(destination),
                        status="ready",
                        approved_at=None,
                        parents_json=parent_ids,
                        metadata_json=metadata or {},
                        created_at=utc_now(),
                    )
                    owned_session.add(artifact)
                    owned_session.flush()
                    if current is None:
                        owned_session.add(
                            ProjectStageHead(
                                project_id=project_id,
                                stage_key=stage_key,
                                artifact_id=artifact_id,
                                approval_status="draft",
                                updated_at=utc_now(),
                            )
                        )
                    else:
                        changed = owned_session.execute(
                            update(ProjectStageHead)
                            .where(
                                ProjectStageHead.project_id == project_id,
                                ProjectStageHead.stage_key == stage_key,
                                ProjectStageHead.artifact_id == expected_head_id,
                            )
                            .values(artifact_id=artifact_id, approval_status="draft", updated_at=utc_now())
                        )
                        if changed.rowcount != 1:
                            raise ArtifactConflict("stage head changed")
                    owned_session.flush()
                    self._fault("before_db_commit")
                    connection.commit()
                    database_committed = True
                except IntegrityError as error:
                    connection.rollback()
                    raise ArtifactConflict("publication collided with a newer head or version") from error
                except Exception:
                    if not database_committed:
                        connection.rollback()
                    raise
                finally:
                    owned_session.close()

            try:
                self._fault("after_db_commit")
            except Exception as error:
                raise ArtifactPublicationCommitted(artifact_id) from error
            assert artifact is not None
            return artifact
        except ArtifactPublicationCommitted:
            raise
        except Exception:
            if not database_committed:
                if staging_path is not None:
                    staging_path.unlink(missing_ok=True)
                if destination is not None:
                    destination.unlink(missing_ok=True)
                if destination_dir is not None:
                    try:
                        destination_dir.rmdir()
                    except OSError:
                        pass
            raise

    def reconcile_orphans(self, project_id: str, min_age_seconds: float = 3600.0) -> list[Path]:
        if not ID_PATTERNS["project"].fullmatch(project_id):
            raise ValueError("project ID is invalid")
        project_root = (self.artifact_root / project_id).resolve()
        if not project_root.is_relative_to(self.artifact_root) or not project_root.is_dir():
            return []
        cutoff = time.time() - max(min_age_seconds, 0.0)
        engine = self._publication_engine()
        with Session(engine) as read_session:
            referenced = set(read_session.scalars(select(Artifact.artifact_id).where(Artifact.project_id == project_id)))
        removed: list[Path] = []
        for child in project_root.iterdir():
            if child.is_dir() and ID_PATTERNS["artifact"].fullmatch(child.name) and child.name not in referenced and child.stat().st_mtime <= cutoff:
                shutil.rmtree(child)
                removed.append(child)
        return removed

    def _publication_engine(self) -> Engine:
        bind = self.session.get_bind()
        if isinstance(bind, Engine):
            return bind
        if isinstance(bind, Connection):
            return bind.engine
        raise RuntimeError("artifact publication requires a SQLAlchemy Engine or Connection")

    def _stage_source(self, staged_path: Path, artifact_id: str) -> tuple[Path, str, int]:
        if self._path_contains_symlink(staged_path):
            raise ValueError("staged artifact source must not contain symlinks")
        source = staged_path.resolve(strict=True)
        if not source.is_file():
            raise ValueError("staged artifact source must be a regular file")
        staging_root = self.artifact_root / ".staging"
        if not staging_root.is_relative_to(self.artifact_root):
            raise ValueError("artifact staging path escapes storage root")
        staging_root.mkdir(parents=True, exist_ok=True)
        temporary = staging_root / f"{artifact_id}.tmp"
        digest = hashlib.sha256()
        size = 0
        try:
            with source.open("rb") as incoming, temporary.open("xb") as outgoing:
                before = os.fstat(incoming.fileno())
                while chunk := incoming.read(1024 * 1024):
                    outgoing.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
                outgoing.flush()
                os.fsync(outgoing.fileno())
                self._fault("after_staging_copy")
                after = os.fstat(incoming.fileno())
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError("staged artifact source changed while copying")
            if temporary.stat().st_size != size or hashlib.sha256(temporary.read_bytes()).hexdigest() != digest.hexdigest():
                raise ValueError("staged artifact integrity check failed")
            return temporary, digest.hexdigest(), size
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    def _validate_request(
        self,
        project_id: str,
        stage_key: str,
        channel_id: str,
        kind: str,
        logical_key: str,
        staged_path: Path,
        expected_head_id: str | None,
        parents: list[str],
        suffix: str,
    ) -> None:
        if not ID_PATTERNS["project"].fullmatch(project_id):
            raise ValueError("project ID is invalid")
        if not ID_PATTERNS["channel"].fullmatch(channel_id):
            raise ValueError("channel ID is invalid")
        if expected_head_id is not None and not ID_PATTERNS["artifact"].fullmatch(expected_head_id):
            raise ValueError("expected head artifact ID is invalid")
        if stage_key not in STAGE_KINDS:
            raise ValueError("artifact stage is unsupported")
        if kind not in STAGE_KINDS[stage_key]:
            raise ValueError("artifact kind is inconsistent with stage")
        if not logical_key or len(logical_key) > 300 or any(character in logical_key for character in "\\/\0"):
            raise ValueError("artifact logical key is invalid")
        if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
            raise ValueError("artifact suffix is invalid")
        if len(parents) != len(set(parents)):
            raise ValueError("artifact parent IDs must be unique")
        if any(not ID_PATTERNS["artifact"].fullmatch(parent_id) for parent_id in parents):
            raise ValueError("artifact parent ID is invalid")
        if staged_path.is_dir():
            raise ValueError("staged artifact source must be a file")

    @staticmethod
    def _validate_parents(session: Session, project_id: str, channel_id: str, parents: list[str]) -> None:
        if not parents:
            return
        rows = list(session.scalars(select(Artifact).where(Artifact.artifact_id.in_(parents))))
        if len(rows) != len(parents) or any(
            row.channel_id != channel_id or row.status != "ready" or (row.project_id is not None and row.project_id != project_id)
            for row in rows
        ):
            raise LookupError("artifact parent not found")

    @staticmethod
    def _path_contains_symlink(path: Path) -> bool:
        candidate = path.absolute()
        while True:
            if candidate.exists() and candidate.is_symlink():
                return True
            if candidate.parent == candidate:
                return False
            candidate = candidate.parent

    def _fault(self, point: str) -> None:
        if self.fault_injector is not None:
            self.fault_injector(point)
