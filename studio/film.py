"""P5 director-to-frame timeline. All intervals are integer frames (inclusive)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FilmError(ValueError):
    pass


class Camera(BaseModel):
    model_config = ConfigDict(extra="forbid")
    zoom: float = Field(ge=0.75, le=2)
    pan_x: float = Field(ge=-200, le=200, default=0)
    pan_y: float = Field(ge=-200, le=200, default=0)


class VoiceCue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1)
    wav: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.wav$")
    start_frame: int = Field(ge=0)


class FilmShot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    shot_id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    duration_frames: int = Field(gt=0)
    rig_id: Literal["baseline", "compact"]
    clip_in: int = Field(ge=0)
    clip_out: int = Field(ge=0)
    camera: Camera
    narration: VoiceCue

    @model_validator(mode="after")
    def local_bounds(self) -> "FilmShot":
        if self.clip_out < self.clip_in:
            raise ValueError("Source clip bounds reversed")
        if self.narration.start_frame >= self.duration_frames:
            raise ValueError("Narration starts outside its shot")
        return self


class FilmPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["film.v1"] = "film.v1"
    fps: Literal[24] = 24
    width: Literal[640] = 640
    height: Literal[480] = 480
    shots: list[FilmShot] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def unique_shots(self) -> "FilmPlan":
        ids = [shot.shot_id for shot in self.shots]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate shot identifiers")
        return self


def compile_film(plan: FilmPlan, clips: dict[str, dict]) -> dict:
    """Expand each shot to a precise global frame sequence; no real-time clock."""
    if not clips:
        raise FilmError("No compiled Spine motion assets")
    timeline = []
    events = []
    shot_manifest = []
    global_start = 0
    last_clip_out = -1
    for shot in plan.shots:
        clip = clips.get(shot.rig_id)
        if clip is None:
            raise FilmError("Unknown rig asset " + shot.rig_id)
        if clip.get("fps") != plan.fps or not isinstance(clip.get("frames"), list):
            raise FilmError("Compiled pose asset fps/frames incompatible")
        if shot.clip_out >= len(clip["frames"]):
            raise FilmError("Shot pose exceeds source motion")
        if shot.clip_in != last_clip_out + 1:
            raise FilmError("Shot sequence must consume source motion contiguously")
        last_clip_out = shot.clip_out
        shots_last = shot.duration_frames - 1
        source_length = shot.clip_out - shot.clip_in
        for local in range(shot.duration_frames):
            clip_index = shot.clip_in + (source_length * local // shots_last if shots_last else source_length)
            timeline.append({"frame": global_start + local, "shot_id": shot.shot_id,
                             "local_frame": local, "clip_frame": clip_index,
                             "rig_id": shot.rig_id, "camera": shot.camera.model_dump()})
        events.append({"shot_id": shot.shot_id,
                       "absolute_frame": global_start + shot.narration.start_frame,
                       "wav": shot.narration.wav, "text": shot.narration.text,
                       "shot_end_frame": global_start + shot.duration_frames})
        shot_manifest.append({"shot_id": shot.shot_id, "start": global_start,
                              "end_exclusive": global_start + shot.duration_frames,
                              "clip_in": shot.clip_in, "clip_out": shot.clip_out})
        global_start += shot.duration_frames
    if last_clip_out != len(clips[plan.shots[-1].rig_id]["frames"]) - 1:
        raise FilmError("Film must consume the complete source action sequence")
    return {"schema_version": "film.timeline.v1", "fps": plan.fps,
            "width": plan.width, "height": plan.height, "total_frames": global_start,
            "duration_seconds": global_start / plan.fps,
            "shots": shot_manifest, "narration": events, "frames": timeline}


def compile_film_file(plan_path: Path, asset_paths: dict[str, Path], output: Path) -> Path:
    plan = FilmPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    clips = {name: json.loads(file.read_text(encoding="utf-8"))
             for name, file in asset_paths.items()}
    result = compile_film(plan, clips)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return output
