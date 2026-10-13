"""Manual ChatGPT/DeepSeek file handoff, without LLM API calls."""
from __future__ import annotations

import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str
    start_frame: int = Field(ge=0)
    end_frame: int = Field(ge=0)
    target: str | None = None

    @model_validator(mode="after")
    def ordering(self) -> "Action":
        if self.end_frame < self.start_frame:
            raise ValueError("end_frame precedes start_frame")
        return self


class Shot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    shot_id: str = Field(min_length=1)
    duration_frames: int = Field(gt=0)
    actions: list[Action] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_timeline(self) -> "Shot":
        if any(a.end_frame >= self.duration_frames for a in self.actions):
            raise ValueError("Action extends beyond shot")
        return self


class AnimationPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = "1.0"
    fps: int = Field(gt=0)
    shots: list[Shot] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self) -> "AnimationPlan":
        ids = [s.shot_id for s in self.shots]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate shot identifiers")
        return self


def import_plan(path: Path) -> AnimationPlan:
    return AnimationPlan.model_validate(json.loads(path.read_text(encoding="utf-8")))


def export_task(prompt: str, catalog: dict, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "Generate strictly valid JSON for the following animation task. "
        "Do not use an API or invent unavailable assets.\n\n"
        + prompt + "\n\nAvailable catalog:\n"
        + json.dumps(catalog, indent=2) + "\n\n"
        + "Output shape: {schema_version:'1.0', fps:24, shots:[{shot_id, duration_frames, actions:[{type,start_frame,end_frame,target?}]}]}",
        encoding="utf-8",
    )
    return destination


def export_motion_task(brief: str, rig: dict, destination: Path) -> Path:
    """Create a copy/paste instruction for ChatGPT/DeepSeek without an LLM API."""
    if not brief.strip():
        raise ValueError("Motion brief cannot be empty")
    destination.parent.mkdir(parents=True, exist_ok=True)
    example = {
        "fps": 24, "frames": 48,
        "shoulder": {"x": 140, "y": 165},
        "rest_hand": {"x": 212, "y": 165},
        "upper_arm": 90, "forearm": 80,
        "initial_prop": {"x": 270, "y": 195},
        "bend": 1,
        "actions": [
            {"kind": "reach", "start": 0, "end": 11, "target": {"x": 270, "y": 195}},
            {"kind": "grab", "start": 12, "end": 14},
            {"kind": "place", "start": 15, "end": 47, "target": {"x": 300, "y": 199}},
        ],
    }
    destination.write_text(
        "You are a 2D motion director. Produce one JSON object only, no markdown. "
        "Follow the P4.1 MotionPlan shape and keep the provided rig geometry. "
        "Actions must be sorted, contiguous, nonoverlapping, start at frame 0 and end at frames-1. "
        "Supported action kinds: reach (target required), grab (no target), "
        "carry (target required), wait (no target), place (target required). "
        "A grab needs hand and free prop to coincide within 1 px. "
        "Carry and place require prior grab; reach while holding is forbidden; "
        "end the shot without holding. All targets must be reachable by the two-link arm. "
        "Do not invent assets, unsupported actions or nonexistent bones.\n\n"
        "Creative request:\n" + brief + "\n\nRig limits and catalog:\n"
        + json.dumps(rig, indent=2) + "\n\nSchema example (adapt coordinates and timing):\n"
        + json.dumps(example, indent=2),
        encoding="utf-8",
    )
    return destination
