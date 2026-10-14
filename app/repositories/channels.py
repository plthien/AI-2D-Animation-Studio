from __future__ import annotations

import hashlib
import os
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import func, select, update
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.hashing import canonical_json
from app.core.time import utc_now
from app.db.models import Artifact, Channel, Project, ProjectStageHead


class ChannelDNAStaleRevision(Exception):
    def __init__(self, current_artifact_id: str | None):
        super().__init__("ChannelDNA revision changed")
        self.current_artifact_id = current_artifact_id


class ChannelDNAPublicationConflict(Exception):
    """A ChannelDNA publication could not be committed consistently."""


class ChannelDNARepository:
    """Publish a channel-scoped DNA revision with one isolated transaction owner."""

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

    def publish(
        self,
        channel_id: str,
        dna: dict,
        hashes: dict[str, str],
        expected_current_artifact_id: str | None,
    ) -> Artifact:
        artifact_id = dna["artifact_id"]
        payload = canonical_json(dna)
        digest = hashlib.sha256(payload).hexdigest()
        staging_root = self.artifact_root / ".staging"
        staging_root.mkdir(parents=True, exist_ok=True)
        temporary = staging_root / f"{artifact_id}.tmp"
        destination_dir = (self.artifact_root / channel_id / artifact_id).resolve()
        if not destination_dir.is_relative_to(self.artifact_root):
            raise ValueError("ChannelDNA artifact path escapes storage root")
        destination = destination_dir / f"{digest}.json"
        database_committed = False
        artifact: Artifact | None = None
        try:
            with temporary.open("xb") as file:
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            if temporary.read_bytes() != payload:
                raise ValueError("ChannelDNA staging integrity check failed")
            self._fault("after_staging")
            destination_dir.mkdir(parents=True, exist_ok=False)
            self._fault("before_finalize")
            os.replace(temporary, destination)
            self._fault("after_finalize")

            engine = self._engine()
            with engine.connect() as connection:
                connection.exec_driver_sql("BEGIN IMMEDIATE")
                owned = Session(bind=connection, expire_on_commit=False, autoflush=False)
                try:
                    channel = owned.get(Channel, channel_id)
                    if channel is None:
                        raise LookupError("channel not found")
                    current_artifact_id = channel.dna_json.get("artifact_id") if channel.dna_json else None
                    if current_artifact_id != expected_current_artifact_id:
                        raise ChannelDNAStaleRevision(current_artifact_id)
                    version = (
                        owned.scalar(
                            select(func.max(Artifact.version)).where(
                                Artifact.channel_id == channel_id,
                                Artifact.logical_key == "channel_dna",
                            )
                        )
                        or 0
                    ) + 1
                    artifact = Artifact(
                        artifact_id=artifact_id,
                        project_id=None,
                        channel_id=channel_id,
                        kind="channel_dna",
                        logical_key="channel_dna",
                        version=version,
                        sha256=f"sha256:{digest}",
                        size_bytes=len(payload),
                        path=str(destination),
                        status="ready",
                        approved_at=utc_now(),
                        parents_json=[current_artifact_id] if current_artifact_id else [],
                        metadata_json=hashes,
                        created_at=utc_now(),
                    )
                    old_hashes = {
                        "visual_style_hash": channel.visual_style_hash,
                        "performance_style_hash": channel.performance_style_hash,
                        "narration_identity_hash": channel.narration_identity_hash,
                    }
                    owned.add(artifact)
                    owned.flush()
                    channel.dna_json = dna
                    channel.visual_style_hash = hashes["visual_style_hash"]
                    channel.performance_style_hash = hashes["performance_style_hash"]
                    channel.narration_identity_hash = hashes["narration_identity_hash"]
                    channel.updated_at = utc_now()
                    if current_artifact_id is not None:
                        self._invalidate_changed_authority(owned, channel_id, old_hashes, hashes)
                    owned.flush()
                    self._fault("before_db_commit")
                    connection.commit()
                    database_committed = True
                except IntegrityError as error:
                    connection.rollback()
                    raise ChannelDNAPublicationConflict("ChannelDNA version publication collided") from error
                except Exception:
                    if not database_committed:
                        connection.rollback()
                    raise
                finally:
                    owned.close()
            self._fault("after_db_commit")
            assert artifact is not None
            return artifact
        except Exception:
            if not database_committed:
                temporary.unlink(missing_ok=True)
                destination.unlink(missing_ok=True)
                try:
                    destination_dir.rmdir()
                except OSError:
                    pass
            raise

    @staticmethod
    def _invalidate_changed_authority(
        session: Session,
        channel_id: str,
        old: dict[str, str | None],
        new: dict[str, str],
    ) -> None:
        stale_keys: set[str] = set()
        if old["visual_style_hash"] != new["visual_style_hash"]:
            stale_keys.update({"authoring", "resolver", "generation", "rigging", "director", "motion", "delivery", "topic", "script", "shot_plan", "animation_plan", "compiled_film", "voice", "final_video"})
        if old["performance_style_hash"] != new["performance_style_hash"]:
            stale_keys.update({"director", "motion", "delivery", "animation_plan", "compiled_film", "final_video"})
        if old["narration_identity_hash"] != new["narration_identity_hash"]:
            stale_keys.update({"authoring", "director", "delivery", "topic", "script", "shot_plan", "voice", "final_video"})
        if not stale_keys:
            return
        project_ids = select(Project.project_id).where(Project.channel_id == channel_id)
        session.execute(
            update(ProjectStageHead)
            .where(
                ProjectStageHead.project_id.in_(project_ids),
                ProjectStageHead.stage_key.in_(stale_keys),
                ProjectStageHead.approval_status.in_(("approved", "draft")),
            )
            .values(approval_status="stale", updated_at=utc_now())
        )

    def _engine(self) -> Engine:
        bind = self.session.get_bind()
        if isinstance(bind, Engine):
            return bind
        if isinstance(bind, Connection):
            return bind.engine
        raise RuntimeError("ChannelDNA publication requires a SQLAlchemy Engine or Connection")

    def _fault(self, point: str) -> None:
        if self.fault_injector is not None:
            self.fault_injector(point)
