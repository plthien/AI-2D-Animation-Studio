from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Body, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.errors import ApiError
from app.api.schemas.base import ChannelCreate, ChannelDNAResponse, ChannelResponse, DataEnvelope, ErrorEnvelope, PageResponse
from app.core.config import get_settings
from app.core.hashing import canonical_json, sha256_bytes
from app.core.ids import new_id
from app.core.time import utc_now
from app.core.strict_json import strict_json_loads
from app.db.dependencies import get_db
from app.db.models import Artifact, Channel
from app.modules.platform.channels import ChannelDNAValidationError, validate_channel_dna

router = APIRouter(prefix="/channels", tags=["channels"], responses={404: {"model": ErrorEnvelope}, 409: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}, 500: {"model": ErrorEnvelope}})


def channel_dict(channel: Channel) -> dict:
    return {"channel_id": channel.channel_id, "name": channel.name, "language": channel.language, "niche": channel.niche, "audience": channel.audience, "created_at": channel.created_at, "updated_at": channel.updated_at}


@router.get("", response_model=DataEnvelope[PageResponse[ChannelResponse]])
def list_channels(page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)) -> dict:
    query = db.scalars(select(Channel).order_by(Channel.created_at.desc(), Channel.channel_id).offset((page - 1) * page_size).limit(min(page_size, 100)))
    total = db.scalar(select(func.count()).select_from(Channel)) or 0
    return {"data": {"items": [channel_dict(channel) for channel in query], "total": total, "page": page, "page_size": min(page_size, 100)}}


@router.post("", status_code=201, response_model=DataEnvelope[ChannelResponse])
def create_channel(body: ChannelCreate, db: Session = Depends(get_db)) -> dict:
    channel = Channel(channel_id=new_id("chn"), name=body.name, language=body.language, niche=body.niche, audience=body.audience, created_at=utc_now(), updated_at=utc_now())
    db.add(channel)
    db.commit()
    return {"data": channel_dict(channel)}


@router.get("/{channel_id}", response_model=DataEnvelope[ChannelResponse])
def get_channel(channel_id: str, db: Session = Depends(get_db)) -> dict:
    channel = db.get(Channel, channel_id)
    if channel is None:
        raise ApiError(404, "CHANNEL_NOT_FOUND", "Channel was not found.")
    return {"data": channel_dict(channel)}


@router.get("/{channel_id}/dna", response_model=DataEnvelope[ChannelDNAResponse])
def get_channel_dna(channel_id: str, db: Session = Depends(get_db)) -> dict:
    channel = db.get(Channel, channel_id)
    if channel is None:
        raise ApiError(404, "CHANNEL_NOT_FOUND", "Channel was not found.")
    return {"data": {"dna": channel.dna_json, "artifact_id": channel.dna_json.get("artifact_id") if channel.dna_json else None, "visual_style_hash": channel.visual_style_hash, "performance_style_hash": channel.performance_style_hash, "narration_identity_hash": channel.narration_identity_hash}}


@router.put("/{channel_id}/dna", response_model=DataEnvelope[ChannelDNAResponse])
async def update_channel_dna(channel_id: str, request: Request, body: dict = Body(...), db: Session = Depends(get_db)) -> dict:
    channel = db.get(Channel, channel_id)
    if channel is None:
        raise ApiError(404, "CHANNEL_NOT_FOUND", "Channel was not found.")
    raw_body = await request.body()
    if len(raw_body) > 10_000_000:
        raise ApiError(413, "REQUEST_TOO_LARGE", "Channel DNA request exceeds the 10 MB limit.")
    try:
        strict_body = strict_json_loads(raw_body)
    except (ValueError, UnicodeDecodeError) as error:
        raise ApiError(422, "CHANNEL_DNA_INVALID", "Request JSON is invalid or contains duplicate keys.", {"path": "$", "recovery": "Send one well-formed JSON object with unique keys."}) from error
    if not isinstance(strict_body, dict):
        raise ApiError(422, "REQUEST_INVALID", "Request body must be an object.", {"path": "$", "recovery": "Send {dna: <channel_dna.v2 object>}."})
    body = strict_body
    if set(body) != {"dna"} or not isinstance(body.get("dna"), dict):
        raise ApiError(422, "REQUEST_INVALID", "Request must contain only an object named dna.", {"path": "$", "recovery": "Send {dna: <channel_dna.v2 object>}."})
    dna = dict(body["dna"])
    if dna.get("schema_version") != "channel_dna.v2":
        raise ApiError(422, "CHANNEL_DNA_VERSION_UNSUPPORTED", "Only channel_dna.v2 is supported.", {"path": "$.schema_version", "recovery": "Submit a channel_dna.v2 document."})
    dna["artifact_id"] = new_id("art")
    try:
        hashes = validate_channel_dna(dna, {"channel_id": channel.channel_id, "name": channel.name, "language": channel.language, "niche": channel.niche, "audience": channel.audience})
    except ChannelDNAValidationError as error:
        raise ApiError(422, error.code, str(error), {"path": error.path, "recovery": "Correct the field to match channel_dna.v2."}) from error
    root = get_settings().artifact_root
    payload = canonical_json(dna)
    digest = sha256_bytes(payload)
    artifact_id = dna["artifact_id"]
    destination_dir = (root / channel_id / artifact_id).resolve()
    if not destination_dir.is_relative_to(root):
        raise ApiError(422, "ARTIFACT_PATH_INVALID", "Artifact path is invalid.")
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{digest.removeprefix('sha256:')}.json"
    if destination.exists():
        raise ApiError(409, "ARTIFACT_IMMUTABLE", "Artifact content already exists and cannot be replaced.")
    temporary = destination.with_suffix(".tmp")
    try:
        with temporary.open("xb") as file:
            file.write(payload)
            file.flush()
            import os
            os.fsync(file.fileno())
        os.replace(temporary, destination)
        version = (db.scalar(select(func.max(Artifact.version)).where(Artifact.channel_id == channel_id, Artifact.logical_key == "channel_dna")) or 0) + 1
        artifact = Artifact(artifact_id=artifact_id, project_id=None, channel_id=channel_id, kind="channel_dna", logical_key="channel_dna", version=version, sha256=digest, size_bytes=len(payload), path=str(destination), status="ready", approved_at=utc_now(), parents_json=[], metadata_json=hashes, created_at=utc_now())
        db.add(artifact)
        channel.dna_json = dna
        channel.visual_style_hash = hashes["visual_style_hash"]
        channel.performance_style_hash = hashes["performance_style_hash"]
        channel.narration_identity_hash = hashes["narration_identity_hash"]
        channel.updated_at = utc_now()
        db.commit()
    except Exception:
        db.rollback()
        temporary.unlink(missing_ok=True)
        destination.unlink(missing_ok=True)
        raise
    return {"data": {"dna": dna, "artifact_id": artifact_id, **hashes}}
