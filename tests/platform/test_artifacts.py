from __future__ import annotations

import pytest
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.ids import new_id
from app.core.time import utc_now
from app.db.models import Artifact, Channel, Project, ProjectStageHead
from app.repositories.artifacts import ArtifactConflict, ArtifactPublicationCommitted, ArtifactRepository


def _project(db_session):
    channel_id, project_id = new_id("chn"), new_id("prj")
    db_session.add(Channel(channel_id=channel_id, name="A", language="en", niche="x", audience="all", created_at=utc_now(), updated_at=utc_now()))
    db_session.add(Project(project_id=project_id, channel_id=channel_id, name="P", description="", status="active", created_at=utc_now(), updated_at=utc_now()))
    db_session.commit()
    return channel_id, project_id


def test_artifact_publication_is_immutable_and_stale_cas_fails(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    staged = tmp_path / "input.json"
    staged.write_text('{"ok":true}', encoding="utf-8")
    repository = ArtifactRepository(db_session, tmp_path / "objects")
    first = repository.publish(project_id, "authoring", channel_id, "script", "script", staged, None)
    original = open(first.path, "rb").read()
    assert first.sha256 == "sha256:" + hashlib.sha256(original).hexdigest()
    second = repository.publish(project_id, "authoring", channel_id, "script", "script", staged, first.artifact_id)
    assert second.version == 2
    assert open(first.path, "rb").read() == original
    head = db_session.get(ProjectStageHead, (project_id, "authoring"))
    head.approval_status = "approved"
    db_session.commit()
    with pytest.raises(ArtifactConflict):
        repository.publish(project_id, "authoring", channel_id, "script", "script", staged, first.artifact_id)
    assert open(first.path, "rb").read() == original
    assert db_session.get(ProjectStageHead, (project_id, "authoring")).artifact_id == second.artifact_id
    assert db_session.get(ProjectStageHead, (project_id, "authoring")).approval_status == "approved"
    assert db_session.get(Artifact, first.artifact_id) is not None


def test_cross_channel_project_publication_is_denied(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    other_channel = new_id("chn")
    db_session.add(Channel(channel_id=other_channel, name="B", language="en", niche="x", audience="all", created_at=utc_now(), updated_at=utc_now()))
    db_session.commit()
    staged = tmp_path / "input.json"
    staged.write_text("{}", encoding="utf-8")
    with pytest.raises(LookupError):
        ArtifactRepository(db_session, tmp_path / "objects").publish(project_id, "authoring", other_channel, "script", "script", staged, None)


def test_artifact_suffix_cannot_escape_storage_root(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    staged = tmp_path / "input.json"
    staged.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        ArtifactRepository(db_session, tmp_path / "objects").publish(project_id, "authoring", channel_id, "script", "script", staged, None, suffix="../../outside")


@pytest.mark.parametrize("_round", range(5))
def test_concurrent_compare_and_set_has_exactly_one_winner(db_session, tmp_path, _round):
    channel_id, project_id = _project(db_session)
    engine = db_session.get_bind()
    staged = tmp_path / "race.json"
    staged.write_text('{"race":true}', encoding="utf-8")

    def publish():
        with Session(engine) as session:
            try:
                artifact = ArtifactRepository(session, tmp_path / "objects").publish(project_id, "authoring", channel_id, "script", "script", staged, None)
                return artifact.artifact_id
            except ArtifactConflict:
                return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _index: publish(), range(2)))
    assert sum(result is not None for result in results) == 1
    winner_id = next(result for result in results if result is not None)
    with Session(engine) as observer:
        assert observer.scalar(select(func.count()).select_from(Artifact)) == 1
        head = observer.get(ProjectStageHead, (project_id, "authoring"))
        assert head is not None and head.artifact_id == winner_id
        winner = observer.get(Artifact, winner_id)
        assert winner is not None and Path(winner.path).read_bytes() == staged.read_bytes()
    artifact_directories = [path for path in (tmp_path / "objects" / project_id).iterdir() if path.is_dir()]
    assert [path.name for path in artifact_directories] == [winner_id]


def test_publish_owns_transaction_without_touching_callers_pending_work(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    pending_channel_id = new_id("chn")
    pending = Channel(
        channel_id=pending_channel_id,
        name="Unrelated pending channel",
        language="en",
        niche="pending",
        audience="all",
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db_session.add(pending)
    with db_session.no_autoflush:
        assert db_session.scalar(select(Project).where(Project.project_id == project_id)) is not None

    staged = tmp_path / "isolated.json"
    staged.write_text('{"isolated":true}', encoding="utf-8")
    published = ArtifactRepository(db_session, tmp_path / "objects").publish(
        project_id,
        "authoring",
        channel_id,
        "script",
        "script",
        staged,
        None,
    )

    with Session(db_session.get_bind()) as observer:
        assert observer.get(Artifact, published.artifact_id) is not None
        assert observer.get(Channel, pending_channel_id) is None
    assert pending in db_session.new
    db_session.rollback()
    with Session(db_session.get_bind()) as observer:
        assert observer.get(Channel, pending_channel_id) is None


def test_parent_ownership_duplicates_stage_kind_and_expected_head_are_validated(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    other_project_id = new_id("prj")
    db_session.add(Project(project_id=other_project_id, channel_id=channel_id, name="Other", description="", status="active", created_at=utc_now(), updated_at=utc_now()))
    db_session.commit()
    staged = tmp_path / "parent.json"
    staged.write_text("{}", encoding="utf-8")
    other_parent = ArtifactRepository(db_session, tmp_path / "objects").publish(
        other_project_id, "authoring", channel_id, "script", "other-script", staged, None
    )
    repository = ArtifactRepository(db_session, tmp_path / "objects")

    with pytest.raises(LookupError):
        repository.publish(project_id, "authoring", channel_id, "script", "script", staged, None, parents=[new_id("art")])
    with pytest.raises(LookupError):
        repository.publish(project_id, "authoring", channel_id, "script", "script", staged, None, parents=[other_parent.artifact_id])
    with pytest.raises(ValueError, match="unique"):
        repository.publish(project_id, "authoring", channel_id, "script", "script", staged, None, parents=[other_parent.artifact_id, other_parent.artifact_id])
    with pytest.raises(ValueError, match="stage"):
        repository.publish(project_id, "impossible", channel_id, "script", "script", staged, None)
    with pytest.raises(ValueError, match="inconsistent"):
        repository.publish(project_id, "authoring", channel_id, "final_video", "script", staged, None)
    with pytest.raises(ValueError, match="expected head"):
        repository.publish(project_id, "authoring", channel_id, "script", "script", staged, "bad-id")


def test_cross_channel_parent_is_rejected(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    other_channel_id, other_project_id = _project(db_session)
    staged = tmp_path / "parent.json"
    staged.write_text("{}", encoding="utf-8")
    other_parent = ArtifactRepository(db_session, tmp_path / "objects").publish(
        other_project_id, "authoring", other_channel_id, "script", "script", staged, None
    )
    with pytest.raises(LookupError):
        ArtifactRepository(db_session, tmp_path / "objects").publish(
            project_id, "authoring", channel_id, "script", "script", staged, None, parents=[other_parent.artifact_id]
        )


def test_symlink_source_and_source_changed_during_copy_are_rejected(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    source = tmp_path / "source.json"
    source.write_text('{"before":true}', encoding="utf-8")
    link = tmp_path / "linked.json"
    try:
        link.symlink_to(source)
    except OSError:
        link = None
    if link is not None:
        with pytest.raises(ValueError, match="symlink"):
            ArtifactRepository(db_session, tmp_path / "objects").publish(
                project_id, "authoring", channel_id, "script", "script", link, None
            )

    def mutate(point: str) -> None:
        if point == "after_staging_copy":
            source.write_text('{"after":false}', encoding="utf-8")
            os.utime(source, None)

    with pytest.raises(ValueError, match="changed while copying"):
        ArtifactRepository(db_session, tmp_path / "objects", mutate).publish(
            project_id, "authoring", channel_id, "script", "script", source, None
        )
    assert db_session.scalar(select(func.count()).select_from(Artifact)) == 0
    assert db_session.get(ProjectStageHead, (project_id, "authoring")) is None


@pytest.mark.parametrize("fault_point", ["after_staging", "before_finalize", "after_finalize", "before_db_commit"])
def test_precommit_faults_leave_no_database_or_final_bytes(db_session, tmp_path, fault_point):
    channel_id, project_id = _project(db_session)
    source = tmp_path / "fault.json"
    source.write_text('{"fault":true}', encoding="utf-8")

    def fail(point: str) -> None:
        if point == fault_point:
            raise RuntimeError(fault_point)

    with pytest.raises(RuntimeError, match=fault_point):
        ArtifactRepository(db_session, tmp_path / "objects", fail).publish(
            project_id, "authoring", channel_id, "script", "script", source, None
        )
    with Session(db_session.get_bind()) as observer:
        assert observer.scalar(select(func.count()).select_from(Artifact)) == 0
        assert observer.get(ProjectStageHead, (project_id, "authoring")) is None
    final_files = list((tmp_path / "objects").glob(f"{project_id}/art_*/*"))
    assert final_files == []


def test_database_constraint_failure_is_typed_and_cleans_attempt(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    source = tmp_path / "constraint.json"
    source.write_text("{}", encoding="utf-8")

    def fail(point: str) -> None:
        if point == "before_db_commit":
            raise IntegrityError("forced", {}, Exception("forced"))

    with pytest.raises(ArtifactConflict):
        ArtifactRepository(db_session, tmp_path / "objects", fail).publish(
            project_id, "authoring", channel_id, "script", "script", source, None
        )
    assert list((tmp_path / "objects").glob(f"{project_id}/art_*/*")) == []


def test_after_commit_fault_is_reconcilable_and_preserves_committed_bytes(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    source = tmp_path / "committed.json"
    expected = b'{"committed":true}'
    source.write_bytes(expected)

    def fail(point: str) -> None:
        if point == "after_db_commit":
            raise RuntimeError("lost response")

    with pytest.raises(ArtifactPublicationCommitted) as raised:
        ArtifactRepository(db_session, tmp_path / "objects", fail).publish(
            project_id, "authoring", channel_id, "script", "script", source, None
        )
    with Session(db_session.get_bind()) as restarted:
        artifact = restarted.get(Artifact, raised.value.artifact_id)
        head = restarted.get(ProjectStageHead, (project_id, "authoring"))
        assert artifact is not None and head is not None and head.artifact_id == artifact.artifact_id
        assert Path(artifact.path).read_bytes() == expected


def test_orphan_reconciliation_removes_only_unreferenced_artifact_directories(db_session, tmp_path):
    channel_id, project_id = _project(db_session)
    source = tmp_path / "keep.json"
    source.write_text("{}", encoding="utf-8")
    repository = ArtifactRepository(db_session, tmp_path / "objects")
    published = repository.publish(project_id, "authoring", channel_id, "script", "script", source, None)
    orphan = tmp_path / "objects" / project_id / new_id("art")
    orphan.mkdir(parents=True)
    (orphan / "orphan.json").write_text("{}", encoding="utf-8")

    removed = repository.reconcile_orphans(project_id, min_age_seconds=0)

    assert removed == [orphan]
    assert not orphan.exists()
    assert Path(published.path).read_bytes() == b"{}"
