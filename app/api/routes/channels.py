from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.errors import ApiError
from app.api.schemas.base import ChannelCreate, ChannelDNAResponse, ChannelDNAUpdate, ChannelResponse, DataEnvelope, ErrorEnvelope, PageResponse
from app.core.config import get_settings
from app.core.ids import new_id
from app.core.time import utc_now
from app.core.strict_json import strict_json_loads
from app.db.dependencies import get_db
from app.db.models import Channel
from app.modules.platform.channels import ChannelDNAValidationError, validate_channel_dna
from app.repositories.channels import ChannelDNAPublicationConflict, ChannelDNARepository, ChannelDNAStaleRevision

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
async def update_channel_dna(channel_id: str, request: Request, body: ChannelDNAUpdate, db: Session = Depends(get_db)) -> dict:
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
    if set(strict_body) != {"dna", "expected_current_artifact_id"} or not isinstance(strict_body.get("dna"), dict):
        raise ApiError(422, "REQUEST_INVALID", "Request must contain dna and expected_current_artifact_id.", {"path": "$", "recovery": "Read the current DNA, then send both required fields."})
    try:
        parsed = ChannelDNAUpdate.model_validate(strict_body)
    except ValueError as error:
        raise ApiError(422, "REQUEST_INVALID", "ChannelDNA revision precondition is invalid.", {"path": "$.expected_current_artifact_id", "recovery": "Send null or an art_<32hex> current artifact ID."}) from error
    dna = dict(parsed.dna)
    if dna.get("schema_version") != "channel_dna.v2":
        raise ApiError(422, "CHANNEL_DNA_VERSION_UNSUPPORTED", "Only channel_dna.v2 is supported.", {"path": "$.schema_version", "recovery": "Submit a channel_dna.v2 document."})
    dna["artifact_id"] = new_id("art")
    try:
        hashes = validate_channel_dna(dna, {"channel_id": channel.channel_id, "name": channel.name, "language": channel.language, "niche": channel.niche, "audience": channel.audience})
    except ChannelDNAValidationError as error:
        raise ApiError(422, error.code, str(error), {"path": error.path, "recovery": "Correct the field to match channel_dna.v2."}) from error
    artifact_id = dna["artifact_id"]
    try:
        ChannelDNARepository(db, get_settings().artifact_root).publish(
            channel_id,
            dna,
            hashes,
            parsed.expected_current_artifact_id,
        )
    except ChannelDNAStaleRevision as error:
        raise ApiError(
            409,
            "CHANNEL_DNA_STALE_REVISION",
            "ChannelDNA changed after it was loaded.",
            {"path": "$.expected_current_artifact_id", "current_artifact_id": error.current_artifact_id, "recovery": "Reload the current DNA, review changes, and retry explicitly."},
        ) from error
    except ChannelDNAPublicationConflict as error:
        raise ApiError(409, "CHANNEL_DNA_PUBLICATION_CONFLICT", "ChannelDNA revision could not be published.", {"path": "$", "recovery": "Reload the current DNA before retrying."}) from error
    return {"data": {"dna": dna, "artifact_id": artifact_id, **hashes}}
