from __future__ import annotations

import pytest
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.base import Base
from app.db import models  # noqa: F401
from app.db.session import make_engine


@pytest.fixture
def db_session(tmp_path: Path):
    engine = make_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()
