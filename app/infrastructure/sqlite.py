from __future__ import annotations

from pathlib import Path

from sqlalchemy.engine import Engine


def ensure_sqlite_parent_dir(engine: Engine) -> None:
    if engine.dialect.name != "sqlite":
        return
    database = engine.url.database
    if database and database != ":memory:":
        Path(database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
