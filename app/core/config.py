from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str
    artifact_root: Path
    host: str
    port: int


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./ai_2d_animation_studio.db"),
        artifact_root=Path(os.getenv("ARTIFACT_ROOT", "./local_artifacts")).resolve(),
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )
