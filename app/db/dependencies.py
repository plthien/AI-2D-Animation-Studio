from __future__ import annotations

from collections.abc import Generator

from app.db.session import SessionLocal


def get_db() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
