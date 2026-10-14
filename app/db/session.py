from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.sqlite_pragmas import configure_sqlite


def make_engine(database_url: str | None = None):
    url = database_url or get_settings().database_url
    kwargs = {"check_same_thread": False, "timeout": 5} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=kwargs, future=True)
    configure_sqlite(engine)
    return engine


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
