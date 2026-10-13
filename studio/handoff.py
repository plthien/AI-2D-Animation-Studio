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
