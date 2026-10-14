from __future__ import annotations

import json
from pathlib import Path


def _channel(client):
    response = client.post("/api/v1/channels", json={"name": "Sample Channel", "language": "en", "niche": "cartoon comedy", "audience": "general"})
    assert response.status_code == 201
    return response.json()["data"]["channel_id"]


def test_channel_dna_v2_validates_and_hashes_identity_domains(client):
    channel_id = _channel(client)
    dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    dna["channel_id"] = channel_id
    response = client.put(f"/api/v1/channels/{channel_id}/dna", json={"dna": dna})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dna"]["schema_version"] == "channel_dna.v2"
    before_visual = data["visual_style_hash"]
    dna["animation_identity"]["motion_energy"] = "high"
    changed = client.put(f"/api/v1/channels/{channel_id}/dna", json={"dna": dna}).json()["data"]
    assert changed["visual_style_hash"] == before_visual
    assert changed["performance_style_hash"] != data["performance_style_hash"]


def test_invalid_v1_dna_rejected_and_channel_not_leaked(client):
    channel_id = _channel(client)
    invalid = client.put(f"/api/v1/channels/{channel_id}/dna", json={"dna": {"schema_version": "channel_dna.v1"}})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "CHANNEL_DNA_VERSION_UNSUPPORTED"
    assert client.get("/api/v1/channels/chn_00000000000000000000000000000000").status_code == 404


def test_channel_dna_rejects_duplicate_json_keys(client):
    channel_id = _channel(client)
    response = client.put(f"/api/v1/channels/{channel_id}/dna", content='{"dna":{"schema_version":"channel_dna.v2","schema_version":"channel_dna.v2"}}', headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "CHANNEL_DNA_INVALID"


def test_projects_share_channel_and_initialize_seven_stage_states(client):
    channel_id = _channel(client)
    first = client.post("/api/v1/projects", json={"channel_id": channel_id, "name": "First", "description": ""})
    second = client.post("/api/v1/projects", json={"channel_id": channel_id, "name": "Second", "description": ""})
    assert first.status_code == second.status_code == 201
    project = first.json()["data"]
    assert len(project["stages"]) == 7
    assert [stage["stage_key"] for stage in project["stages"]] == ["authoring", "resolver", "generation", "rigging", "director", "motion", "delivery"]
    assert [stage["status"] for stage in project["stages"]] == ["blocked"] * 7
    assert client.get(f"/api/v1/projects/{project['project_id']}").status_code == 200
    assert client.get("/api/v1/projects/prj_00000000000000000000000000000000/artifacts").status_code == 404


def test_valid_dna_unblocks_authoring_only_and_invalid_wpm_is_rejected(client):
    channel_id = _channel(client)
    dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    dna["channel_id"] = channel_id
    dna["narration"]["wpm_min"] = dna["narration"]["wpm_max"]
    invalid = client.put(f"/api/v1/channels/{channel_id}/dna", json={"dna": dna})
    assert invalid.status_code == 422
    dna["narration"]["wpm_min"] = 140
    assert client.put(f"/api/v1/channels/{channel_id}/dna", json={"dna": dna}).status_code == 200
    project = client.post("/api/v1/projects", json={"channel_id": channel_id, "name": "Ready for authoring", "description": ""}).json()["data"]
    assert [stage["status"] for stage in project["stages"]] == ["ready", "blocked", "blocked", "blocked", "blocked", "blocked", "blocked"]


def test_health_error_envelopes_and_openapi(client):
    assert client.get("/health").json() == {"data": {"status": "ok", "schema_version": "1"}}
    bad = client.post("/api/v1/channels", json={"name": ""})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "REQUEST_INVALID"
    assert client.get("/api/v1/channels?page=-1").status_code == 422
    schema = client.get("/openapi.json").json()
    assert "/api/v1/projects" in schema["paths"]
