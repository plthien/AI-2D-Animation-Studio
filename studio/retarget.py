"""Retarget an authored motion plan to different verified Spine character rigs.

Retargeting is actor-local: the original wrist path is expressed relative to
the authored shoulder and scaled by total arm reach. A prop's CONTACT SOCKET
offset is kept in screen pixels (same physical prop) instead of scaled.
This does not solve stationary-world props or multi-actor interactions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from studio.motion import MotionError, MotionPlan, Point, compile_motion


class BoneRoles(BaseModel):
    model_config = ConfigDict(extra="forbid")
    upper_arm: str = Field(min_length=1)
    forearm: str = Field(min_length=1)
    hand: str = Field(min_length=1)

    @model_validator(mode="after")
    def distinct_roles(self) -> "BoneRoles":
        if len({self.upper_arm, self.forearm, self.hand}) != 3:
            raise ValueError("Bone roles must be distinct")
        return self


class RigProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"] = "1.0"
    rig_id: str = Field(min_length=1)
    bones: BoneRoles
    actor_origin: Point
    shoulder: Point
    upper_arm: FiniteFloat = Field(gt=0)
    forearm: FiniteFloat = Field(gt=0)
    grip_offset: Point = Field(default_factory=lambda: Point(x=0, y=0))


def validate_spine_profile(profile: RigProfile, skeleton: dict) -> None:
    """Fail closed on absent/wrong-chain/length-mismatched Spine bones."""
    bones = {bone["name"]: bone for bone in skeleton.get("bones", [])}
    names = (profile.bones.upper_arm, profile.bones.forearm, profile.bones.hand)
    if any(name not in bones for name in names):
        raise MotionError("RigProfile bone role missing from Spine skeleton")
    upper, lower, hand = (bones[name] for name in names)
    if lower.get("parent") != profile.bones.upper_arm or hand.get("parent") != profile.bones.forearm:
        raise MotionError("RigProfile bone chain does not match skeleton hierarchy")
    if abs(float(lower.get("x", 0)) - profile.upper_arm) > 0.01 or abs(float(hand.get("x", 0)) - profile.forearm) > 0.01:
        raise MotionError("RigProfile limb lengths do not match Spine joints")
    if abs(float(lower.get("y", 0))) > 0.01 or abs(float(hand.get("y", 0))) > 0.01:
        raise MotionError("RigProfile requires zero-offset straight setup arm chain")
    if any(abs(float(bone.get("rotation", 0))) > 0.01 or
           abs(float(bone.get("scaleX", 1)) - 1) > 0.01 or
           abs(float(bone.get("scaleY", 1)) - 1) > 0.01
           for bone in (upper, lower, hand)):
        raise MotionError("RigProfile requires neutral setup rotations and unit bone scales")


def retarget_motion(source: MotionPlan, profile: RigProfile) -> MotionPlan:
    """Scale wrist trajectory about source shoulder; keep cup socket dimensions."""
    scale = (profile.upper_arm + profile.forearm) / (source.upper_arm + source.forearm)

    def translate(point: Point) -> Point:
        return Point(x=profile.shoulder.x + (point.x - source.shoulder.x) * scale,
                     y=profile.shoulder.y + (point.y - source.shoulder.y) * scale)

    grip_hand = Point(x=source.initial_prop.x - source.grip_offset.x,
                      y=source.initial_prop.y - source.grip_offset.y)
    mapped_hand = translate(grip_hand)
    mapped_prop = Point(x=mapped_hand.x + profile.grip_offset.x,
                        y=mapped_hand.y + profile.grip_offset.y)
    actions = [action.model_copy(update={"target": translate(action.target)}) if action.target is not None else action
               for action in source.actions]
    return source.model_copy(update={
        "shoulder": profile.shoulder,
        "rest_hand": translate(source.rest_hand),
        "upper_arm": profile.upper_arm,
        "forearm": profile.forearm,
        "initial_prop": mapped_prop,
        "grip_offset": profile.grip_offset,
        "actions": actions,
    })


def compile_retargeted(source: MotionPlan, profile: RigProfile, skeleton: dict) -> dict:
    """Validate actual Spine skeleton, retarget, then compile and enforce IK."""
    validate_spine_profile(profile, skeleton)
    transformed = retarget_motion(source, profile)
    compiled = compile_motion(transformed)
    compiled["rig"] = profile.model_dump()
    compiled["retarget"] = {"mode": "actor_local", "reach_scale":
                            (profile.upper_arm + profile.forearm) / (source.upper_arm + source.forearm)}
    return compiled


def compile_retargeted_file(source: Path, profile: Path, skeleton: Path, output: Path) -> Path:
    motion = MotionPlan.model_validate_json(source.read_text(encoding="utf-8"))
    rig = RigProfile.model_validate_json(profile.read_text(encoding="utf-8"))
    built = compile_retargeted(motion, rig, json.loads(skeleton.read_text(encoding="utf-8")))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(built, indent=2), encoding="utf-8")
    return output
