from __future__ import annotations

from sqlalchemy import inspect

from app.core.ids import new_id
from app.core.time import utc_now
from app.db.models import Channel, Project


def test_database_has_fourteen_required_tables(db_session):
    tables = set(inspect(db_session.get_bind()).get_table_names())
    assert tables == {"channels", "projects", "project_stage_heads", "artifacts", "authoring_reservations", "assets", "asset_versions", "project_asset_bindings", "rigs", "rig_versions", "motion_templates", "operations", "operation_tasks", "jobs"}


def test_one_channel_can_own_two_projects_and_survives_session_restart(db_session):
    channel_id = new_id("chn")
    db_session.add(Channel(channel_id=channel_id, name="A", language="en", niche="cartoon", audience="general", created_at=utc_now(), updated_at=utc_now()))
    db_session.flush()
    first, second = new_id("prj"), new_id("prj")
    db_session.add_all([Project(project_id=first, channel_id=channel_id, name="One", description="", status="active", created_at=utc_now(), updated_at=utc_now()), Project(project_id=second, channel_id=channel_id, name="Two", description="", status="active", created_at=utc_now(), updated_at=utc_now())])
    db_session.commit()
    assert db_session.get(Project, first).channel_id == channel_id
    assert db_session.get(Project, second).channel_id == channel_id
    with db_session.get_bind().connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1


def test_persisted_project_survives_engine_restart(tmp_path):
    from sqlalchemy.orm import Session
    from app.db.base import Base
    from app.db.session import make_engine

    url = f"sqlite:///{(tmp_path / 'restart.db').as_posix()}"
    first_engine = make_engine(url)
    Base.metadata.create_all(first_engine)
    channel_id, project_id = new_id("chn"), new_id("prj")
    with Session(first_engine) as session:
        session.add(Channel(channel_id=channel_id, name="Persist", language="en", niche="x", audience="all", created_at=utc_now(), updated_at=utc_now()))
        session.add(Project(project_id=project_id, channel_id=channel_id, name="Saved", description="", status="active", created_at=utc_now(), updated_at=utc_now()))
        session.commit()
    first_engine.dispose()
    second_engine = make_engine(url)
    with Session(second_engine) as session:
        assert session.get(Project, project_id).name == "Saved"
    second_engine.dispose()
