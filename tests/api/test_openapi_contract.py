from __future__ import annotations

import json
from pathlib import Path

from app.main import app


ROOT = Path(__file__).resolve().parents[2]


def test_committed_openapi_matches_application() -> None:
    committed = json.loads((ROOT / "openapi.json").read_text(encoding="utf-8"))
    assert committed == app.openapi()


def test_channel_dna_revision_precondition_is_required() -> None:
    schema = app.openapi()
    update = schema["components"]["schemas"]["ChannelDNAUpdate"]
    assert set(update["required"]) == {"dna", "expected_current_artifact_id"}
    put = schema["paths"]["/api/v1/channels/{channel_id}/dna"]["put"]
    assert put["requestBody"]["required"] is True
    assert put["responses"]["409"]["content"]["application/json"]["schema"]["$ref"].endswith("/ErrorEnvelope")
