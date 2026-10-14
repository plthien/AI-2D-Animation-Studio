from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db import models  # noqa: F401
from app.db.dependencies import get_db
from app.db.session import make_engine
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    artifact_root = tmp_path / "artifacts"
    monkeypatch.setenv("ARTIFACT_ROOT", str(artifact_root))
    engine = make_engine(f"sqlite:///{(tmp_path / 'api.db').as_posix()}")
    Base.metadata.create_all(engine)
    def override_db():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_db] = override_db
    test_client = TestClient(app)
    test_client.p0_engine = engine
    test_client.p0_artifact_root = artifact_root
    yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
