from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


REQUIRED = {"channels", "projects", "project_stage_heads", "artifacts", "authoring_reservations", "assets", "asset_versions", "project_asset_bindings", "rigs", "rig_versions", "motion_templates", "operations", "operation_tasks", "jobs"}


def test_alembic_fresh_database_creates_exact_fourteen_tables(tmp_path, monkeypatch):
    database = tmp_path / "migration.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database.as_posix()}")
    root = Path(__file__).resolve().parents[2]
    config = Config(str(root / "alembic.ini"))
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database.as_posix()}")
    try:
        names = set(inspect(engine).get_table_names()) - {"alembic_version"}
        assert names == REQUIRED
        assert inspect(engine).get_foreign_keys("projects")
    finally:
        engine.dispose()
