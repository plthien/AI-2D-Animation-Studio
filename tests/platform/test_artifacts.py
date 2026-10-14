from __future__ import annotations

import pytest
from concurrent.futures import ThreadPoolExecutor
import hashlib
from sqlalchemy.orm import Session

from app.core.ids import new_id
from app.core.time import utc_now
from app.db.models import Artifact, Channel, Project, ProjectStageHead
from app.repositories.artifacts import ArtifactConflict, ArtifactRepository


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


def test_concurrent_compare_and_set_has_exactly_one_winner(db_session, tmp_path):
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
