from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from app.core.hashing import content_hash

DNA_SCHEMA = Path(__file__).resolve().parents[3] / "contracts" / "schemas" / "channel_dna.schema.json"


class ChannelDNAValidationError(ValueError):
    def __init__(self, message: str, path: str, code: str = "CHANNEL_DNA_INVALID"):
        super().__init__(message)
        self.path = path
        self.code = code


def validate_channel_dna(dna: dict[str, Any], channel: dict[str, str]) -> dict[str, str]:
    schema = json.loads(DNA_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dna), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        path = "$" + "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path)
        raise ChannelDNAValidationError("Channel DNA does not match the channel_dna.v2 schema.", path)
    if dna["narration"]["wpm_min"] >= dna["narration"]["wpm_max"]:
        raise ChannelDNAValidationError("wpm_min must be less than wpm_max.", "$.narration")
    if dna["channel_id"] != channel["channel_id"] or any(dna["channel"][key] != channel[key] for key in ("name", "language", "niche", "audience")):
        raise ChannelDNAValidationError("Channel DNA identity must match its owning channel.", "$.channel", "CHANNEL_DNA_IDENTITY_MISMATCH")
    return {
        "visual_style_hash": content_hash({"visual_identity": dna["visual_identity"], "entity_styles": dna["entity_styles"], "global_negative_constraints": dna["global_negative_constraints"]}),
        "performance_style_hash": content_hash({"animation_identity": dna["animation_identity"], "editorial_identity": dna["editorial_identity"]}),
        "narration_identity_hash": content_hash({"narration": dna["narration"], "narration_identity": dna["narration_identity"]}),
    }
