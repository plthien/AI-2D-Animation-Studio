from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.ids import new_id
from app.db.models import Artifact, Channel, ProjectStageHead
from app.modules.platform.channels import validate_channel_dna
from app.repositories.channels import ChannelDNARepository


def _channel(client):
    response = client.post("/api/v1/channels", json={"name": "Sample Channel", "language": "en", "niche": "cartoon comedy", "audience": "general"})
    assert response.status_code == 201
    return response.json()["data"]["channel_id"]


def _save_dna(client, channel_id, dna, expected_current_artifact_id=None):
    return client.put(
        f"/api/v1/channels/{channel_id}/dna",
        json={"dna": dna, "expected_current_artifact_id": expected_current_artifact_id},
    )


def test_channel_dna_v2_validates_and_hashes_identity_domains(client):
    channel_id = _channel(client)
    dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    dna["channel_id"] = channel_id
    response = _save_dna(client, channel_id, dna)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dna"]["schema_version"] == "channel_dna.v2"
    before_visual = data["visual_style_hash"]
    dna["animation_identity"]["motion_energy"] = "high"
    changed = _save_dna(client, channel_id, dna, data["artifact_id"]).json()["data"]
    assert changed["visual_style_hash"] == before_visual
    assert changed["performance_style_hash"] != data["performance_style_hash"]


def test_invalid_v1_dna_rejected_and_channel_not_leaked(client):
    channel_id = _channel(client)
    invalid = _save_dna(client, channel_id, {"schema_version": "channel_dna.v1"})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "CHANNEL_DNA_VERSION_UNSUPPORTED"
    assert client.get("/api/v1/channels/chn_00000000000000000000000000000000").status_code == 404


def test_channel_dna_rejects_wrong_identity_and_unexpected_request_fields(client):
    channel_id = _channel(client)
    dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    dna["channel_id"] = "chn_00000000000000000000000000000000"
    wrong = _save_dna(client, channel_id, dna)
    assert wrong.status_code == 422
    assert wrong.json()["error"]["code"] == "CHANNEL_DNA_IDENTITY_MISMATCH"
    dna["channel_id"] = channel_id
    extra = client.put(f"/api/v1/channels/{channel_id}/dna", json={"dna": dna, "expected_current_artifact_id": None, "overwrite": True})
    assert extra.status_code == 422
    assert extra.json()["error"]["code"] == "REQUEST_INVALID"


def test_channel_dna_rejects_duplicate_json_keys(client):
    channel_id = _channel(client)
    response = client.put(f"/api/v1/channels/{channel_id}/dna", content='{"dna":{"schema_version":"channel_dna.v2","schema_version":"channel_dna.v2"},"expected_current_artifact_id":null}', headers={"Content-Type": "application/json"})
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
    invalid = _save_dna(client, channel_id, dna)
    assert invalid.status_code == 422
    dna["narration"]["wpm_min"] = 140
    assert _save_dna(client, channel_id, dna).status_code == 200
    project = client.post("/api/v1/projects", json={"channel_id": channel_id, "name": "Ready for authoring", "description": ""}).json()["data"]
    assert [stage["status"] for stage in project["stages"]] == ["ready", "blocked", "blocked", "blocked", "blocked", "blocked", "blocked"]


def test_health_error_envelopes_and_openapi(client):
    assert client.get("/health").json() == {"data": {"status": "ok", "schema_version": "1"}}
    bad = client.post("/api/v1/channels", json={"name": ""})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "REQUEST_INVALID"
    assert client.get("/api/v1/channels?page=-1").status_code == 422
    schema = client.get("/openapi.json").json()
    assert "/api/v1/projects" in schema["paths"]


def test_channel_dna_requires_revision_precondition_and_preserves_history(client):
    channel_id = _channel(client)
    dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    dna["channel_id"] = channel_id
    missing = client.put(f"/api/v1/channels/{channel_id}/dna", json={"dna": dna})
    assert missing.status_code == 422

    created = _save_dna(client, channel_id, dna)
    assert created.status_code == 200
    first = created.json()["data"]
    first_path = Path(first["dna"]["artifact_id"])
    with Session(client.p0_engine) as session:
        first_artifact = session.get(Artifact, first["artifact_id"])
        assert first_artifact is not None
        first_path = Path(first_artifact.path)
        first_bytes = first_path.read_bytes()

    stale_null = _save_dna(client, channel_id, dna)
    assert stale_null.status_code == 409
    assert stale_null.json()["error"]["code"] == "CHANNEL_DNA_STALE_REVISION"
    assert stale_null.json()["error"]["details"]["current_artifact_id"] == first["artifact_id"]

    dna["narration_identity"]["delivery"] = ["A revised delivery rule."]
    updated = _save_dna(client, channel_id, dna, first["artifact_id"])
    assert updated.status_code == 200
    second = updated.json()["data"]
    assert second["artifact_id"] != first["artifact_id"]
    assert second["narration_identity_hash"] != first["narration_identity_hash"]
    assert second["visual_style_hash"] == first["visual_style_hash"]
    assert second["performance_style_hash"] == first["performance_style_hash"]
    assert first_path.read_bytes() == first_bytes
    assert client.get(f"/api/v1/channels/{channel_id}/dna").json()["data"]["artifact_id"] == second["artifact_id"]
    with Session(client.p0_engine) as session:
        versions = list(session.scalars(select(Artifact.version).where(Artifact.channel_id == channel_id, Artifact.kind == "channel_dna").order_by(Artifact.version)))
        assert versions == [1, 2]


def test_concurrent_channel_dna_updates_have_one_winner_and_one_typed_stale_conflict(client):
    channel_id = _channel(client)
    base_dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    base_dna["channel_id"] = channel_id
    initial = _save_dna(client, channel_id, base_dna).json()["data"]

    def update(index: int):
        candidate = json.loads(json.dumps(base_dna))
        candidate["animation_identity"]["reaction_hold_frames"] = 10 + index
        return _save_dna(client, channel_id, candidate, initial["artifact_id"])

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(update, range(2)))
    assert sorted(response.status_code for response in responses) == [200, 409]
    loser = next(response for response in responses if response.status_code == 409)
    assert loser.json()["error"]["code"] == "CHANNEL_DNA_STALE_REVISION"
    active = client.get(f"/api/v1/channels/{channel_id}/dna").json()["data"]
    assert loser.json()["error"]["details"]["current_artifact_id"] == active["artifact_id"]
    with Session(client.p0_engine) as session:
        assert session.scalar(select(func.count()).select_from(Artifact).where(Artifact.channel_id == channel_id, Artifact.kind == "channel_dna")) == 2


def test_performance_only_dna_change_does_not_stale_visual_stage_heads(client):
    channel_id = _channel(client)
    dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    dna["channel_id"] = channel_id
    initial = _save_dna(client, channel_id, dna).json()["data"]
    project = client.post("/api/v1/projects", json={"channel_id": channel_id, "name": "Stages", "description": ""}).json()["data"]
    with Session(client.p0_engine) as session:
        artifact = session.get(Artifact, initial["artifact_id"])
        session.add(ProjectStageHead(project_id=project["project_id"], stage_key="generation", artifact_id=artifact.artifact_id, approval_status="approved", updated_at=artifact.created_at))
        session.add(ProjectStageHead(project_id=project["project_id"], stage_key="director", artifact_id=artifact.artifact_id, approval_status="approved", updated_at=artifact.created_at))
        session.commit()

    dna["animation_identity"]["motion_energy"] = "high"
    changed = _save_dna(client, channel_id, dna, initial["artifact_id"])
    assert changed.status_code == 200
    with Session(client.p0_engine) as session:
        assert session.get(ProjectStageHead, (project["project_id"], "generation")).approval_status == "approved"
        assert session.get(ProjectStageHead, (project["project_id"], "director")).approval_status == "stale"


def test_visual_hash_changes_without_changing_performance_or_narration_hashes(client):
    channel_id = _channel(client)
    dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    dna["channel_id"] = channel_id
    first = _save_dna(client, channel_id, dna).json()["data"]
    dna["visual_identity"]["palette"] = "ochre, cream, charcoal, and muted blue"
    second = _save_dna(client, channel_id, dna, first["artifact_id"]).json()["data"]
    assert second["visual_style_hash"] != first["visual_style_hash"]
    assert second["performance_style_hash"] == first["performance_style_hash"]
    assert second["narration_identity_hash"] == first["narration_identity_hash"]


def test_channel_dna_fault_before_commit_rolls_back_database_and_attempt_files(client):
    channel_id = _channel(client)
    dna = json.loads((Path(__file__).resolve().parents[2] / "contracts/examples/channel_dna.json").read_text(encoding="utf-8"))
    dna["channel_id"] = channel_id
    first = _save_dna(client, channel_id, dna).json()["data"]
    dna["artifact_id"] = new_id("art")
    attempted_id = dna["artifact_id"]
    dna["animation_identity"]["reaction_hold_frames"] = 15
    with Session(client.p0_engine) as session:
        channel = session.get(Channel, channel_id)
        hashes = validate_channel_dna(dna, {"channel_id": channel.channel_id, "name": channel.name, "language": channel.language, "niche": channel.niche, "audience": channel.audience})

        def fail(point: str) -> None:
            if point == "before_db_commit":
                raise RuntimeError("injected precommit fault")

        try:
            ChannelDNARepository(session, client.p0_artifact_root, fail).publish(channel_id, dna, hashes, first["artifact_id"])
        except RuntimeError as error:
            assert str(error) == "injected precommit fault"
        else:
            raise AssertionError("fault injection did not fire")

    with Session(client.p0_engine) as session:
        channel = session.get(Channel, channel_id)
        assert channel.dna_json["artifact_id"] == first["artifact_id"]
        assert session.get(Artifact, attempted_id) is None
    assert not (client.p0_artifact_root / channel_id / attempted_id).exists()
