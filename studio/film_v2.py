"""P5/P6 production-shaped shot compiler: each shot owns its actual motion and assets.

No dependence on legacy 48-pose shared clip or hardcoded coffee-story labels.
All media IDs resolve through an explicit catalog; no arbitrary paths in director
JSON. Boundaries remain absolute 24-FPS frames; there is no silent motion stretching.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from studio.film import Camera, FilmError, VoiceCue

ID = r"^[a-z][a-z0-9_]*$"
FILE = r"^[a-z][a-z0-9_/-]*\.png$"


class RigAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")
    directory: str = Field(pattern=ID)


class ImageAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")
    image: str = Field(pattern=FILE)


class AssetCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rigs: dict[str, RigAsset] = Field(min_length=1)
    backgrounds: dict[str, ImageAsset] = Field(min_length=1)
    props: dict[str, ImageAsset] = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_ids(self) -> "AssetCatalog":
        for group in (self.rigs, self.backgrounds, self.props):
            if any(not __import__("re").fullmatch(ID, key) for key in group):
                raise ValueError("Asset catalog ID is invalid")
        return self


class ActorTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")
    actor_id: str = Field(pattern=ID)
    rig_id: str = Field(pattern=ID)
    motion_id: str = Field(pattern=ID)
    offset_x: float = Field(default=0, ge=-640, le=640)
    offset_y: float = Field(default=0, ge=-480, le=480)
    layer: int = Field(default=0, ge=-20, le=20)


class PropTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prop_id: str = Field(pattern=ID)
    visual_id: str = Field(pattern=ID)
    owner_actor_id: str = Field(pattern=ID)
    layer: int = Field(default=10, ge=-20, le=20)


class ShotV2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    shot_id: str = Field(pattern=ID)
    duration_frames: int = Field(gt=0, le=2400)
    background_id: str = Field(pattern=ID)
    camera: Camera
    actors: list[ActorTrack] = Field(min_length=1, max_length=6)
    props: list[PropTrack] = Field(default_factory=list, max_length=6)
    narration: VoiceCue | None = None
    continuity_break: bool = False

    @model_validator(mode="after")
    def valid_tracks(self) -> "ShotV2":
        actors = [actor.actor_id for actor in self.actors]
        props = [prop.prop_id for prop in self.props]
        owners = [prop.owner_actor_id for prop in self.props]
        if len(set(actors)) != len(actors) or len(set(props)) != len(props):
            raise ValueError("Duplicate actor or prop ID in shot")
        if len(set(owners)) != len(owners):
            raise ValueError("One active prop per actor is supported")
        if any(owner not in actors for owner in owners):
            raise ValueError("Prop owner missing in shot")
        if self.narration is not None and self.narration.start_frame >= self.duration_frames:
            raise ValueError("Narration starts outside shot")
        return self


class FilmPlanV2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["film.v2"] = "film.v2"
    fps: Literal[24] = 24
    width: int = Field(default=640, ge=320, le=1920)
    height: int = Field(default=480, ge=240, le=1080)
    shots: list[ShotV2] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def unique_shots(self) -> "FilmPlanV2":
        ids = [shot.shot_id for shot in self.shots]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate shot IDs")
        return self


def _pose(clip: dict, index: int) -> dict:
    pose = clip["frames"][index]
    if not isinstance(pose, dict) or pose.get("frame") != index:
        raise FilmError("Motion frame index mismatch")
    for key in ("shoulder", "elbow", "hand", "prop", "prop_state"):
        if key not in pose:
            raise FilmError("Incomplete rig pose / prop contract")
    return pose


def compile_film_v2(plan: FilmPlanV2, catalog: AssetCatalog, motions: dict[str, dict]) -> dict:
    """Compile asset-bound timeline with exact shot-local frame IDs and continuity checks."""
    if not motions:
        raise FilmError("No motion clips provided")
    timeline, shots, narration = [], [], []
    start = 0
    previous: ShotV2 | None = None
    for shot in plan.shots:
        if shot.background_id not in catalog.backgrounds:
            raise FilmError("Unknown shot background " + shot.background_id)
        active = {}
        for actor in shot.actors:
            if actor.rig_id not in catalog.rigs:
                raise FilmError("Unknown Spine rig " + actor.rig_id)
            if actor.motion_id not in motions:
                raise FilmError("Unknown motion clip " + actor.motion_id)
            clip = motions[actor.motion_id]
            if (clip.get("fps") != plan.fps or clip.get("duration_frames") != shot.duration_frames
                    or not isinstance(clip.get("frames"), list)
                    or len(clip["frames"]) != shot.duration_frames):
                raise FilmError("Motion clip frame count / FPS mismatch: " + actor.motion_id)
            if clip.get("rig_id") != actor.rig_id:
                raise FilmError("Motion clip rig identity mismatch")
            _pose(clip, 0)
            _pose(clip, shot.duration_frames - 1)
            active[actor.actor_id] = actor
        for prop in shot.props:
            if prop.visual_id not in catalog.props:
                raise FilmError("Unknown prop visual " + prop.visual_id)
        # Compare world-space prop centers and wrist pose when actors continue
        # in consecutive shots. A consciously authored jump cut must opt out.
        if previous is not None and not shot.continuity_break:
            prior_actors = {actor.actor_id: actor for actor in previous.actors}
            prior_props = {prop.prop_id: prop for prop in previous.props}
            for actor in shot.actors:
                before = prior_actors.get(actor.actor_id)
                if before is not None:
                    p = _pose(motions[before.motion_id], previous.duration_frames - 1)["hand"]
                    q = _pose(motions[actor.motion_id], 0)["hand"]
                    if abs(p["x"] + before.offset_x - q["x"] - actor.offset_x) > 0.75 or abs(p["y"] + before.offset_y - q["y"] - actor.offset_y) > 0.75:
                        raise FilmError("Actor wrist jumps at shot boundary")
            for prop in shot.props:
                before_prop = prior_props.get(prop.prop_id)
                if before_prop is not None:
                    prev_actor = prior_actors[before_prop.owner_actor_id]
                    next_actor = active[prop.owner_actor_id]
                    a = _pose(motions[prev_actor.motion_id], previous.duration_frames - 1)["prop"]
                    b = _pose(motions[next_actor.motion_id], 0)["prop"]
                    if (abs(a["x"] + prev_actor.offset_x - b["x"] - next_actor.offset_x) > 0.75
                            or abs(a["y"] + prev_actor.offset_y - b["y"] - next_actor.offset_y) > 0.75):
                        raise FilmError("World prop jumps at shot boundary")
        if shot.narration is not None:
            narration.append({"shot_id": shot.shot_id, "absolute_frame": start + shot.narration.start_frame,
                              "shot_end_frame": start + shot.duration_frames, "wav": shot.narration.wav,
                              "text": shot.narration.text})
        for local_frame in range(shot.duration_frames):
            timeline.append({
                "frame": start + local_frame, "shot_id": shot.shot_id,
                "local_frame": local_frame, "background_id": shot.background_id,
                "camera": shot.camera.model_dump(),
                "actors": [dict(actor.model_dump(), pose_frame=local_frame) for actor in shot.actors],
                "props": [prop.model_dump() for prop in shot.props],
            })
        shots.append({"shot_id": shot.shot_id, "start": start,
                      "end_exclusive": start + shot.duration_frames,
                      "motion_ids": [actor.motion_id for actor in shot.actors],
                      "background_id": shot.background_id})
        start += shot.duration_frames
        previous = shot
    return {"schema_version": "film.timeline.v2", "fps": plan.fps,
            "width": plan.width, "height": plan.height, "total_frames": start,
            "duration_seconds": start / plan.fps, "assets": catalog.model_dump(),
            "shots": shots, "narration": narration, "frames": timeline}


def compile_film_v2_file(plan_file: Path, catalog_file: Path, clips_file: Path, destination: Path) -> Path:
    plan = FilmPlanV2.model_validate_json(plan_file.read_text(encoding="utf-8"))
    catalog = AssetCatalog.model_validate_json(catalog_file.read_text(encoding="utf-8"))
    motions = json.loads(clips_file.read_text(encoding="utf-8"))
    compiled = compile_film_v2(plan, catalog, motions)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(compiled, indent=2), encoding="utf-8")
    return destination
