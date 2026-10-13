"""Deterministic, fail-closed two-bone contact planner (P4 prototype).

Coordinates use screen pixels (x right, y down). This module produces
immutable-per-frame data, without writing animation source code for each shot.
Only one actor/prop and a two-bone arm are supported in this P4 vertical slice.
"""
from __future__ import annotations

from math import acos, atan2, cos, hypot, sin
from pathlib import Path
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

EPSILON = 1e-6
MOVE_ACTIONS = frozenset({"reach", "carry", "place"})


class MotionError(ValueError):
    """Reject unsatisfiable or invalid choreography."""


class Point(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: FiniteFloat
    y: FiniteFloat


class MotionAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["reach", "grab", "carry", "place", "wait"]
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    target: Point | None = None

    @model_validator(mode="after")
    def validate_action(self) -> "MotionAction":
        if self.end < self.start:
            raise ValueError("Action ends before it starts")
        if (self.kind in MOVE_ACTIONS) != (self.target is not None):
            raise ValueError("Target required only for movement actions")
        return self


class MotionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fps: int = Field(gt=0)
    frames: int = Field(gt=0, le=2400)
    shoulder: Point
    rest_hand: Point
    upper_arm: FiniteFloat = Field(gt=0)
    forearm: FiniteFloat = Field(gt=0)
    initial_prop: Point
    grip_offset: Point = Field(default_factory=lambda: Point(x=0, y=0))
    bend: Literal[-1, 1] = 1
    actions: list[MotionAction] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_sequence(self) -> "MotionPlan":
        next_frame = 0
        for action in self.actions:
            if action.start != next_frame:
                raise ValueError("Actions must be contiguous, sorted and start at 0")
            next_frame = action.end + 1
        if next_frame != self.frames:
            raise ValueError("Actions must span exactly the requested frames")
        return self


def solve_two_bone(shoulder: Point, target: Point, upper: float, lower: float, bend: int) -> Point:
    """Return elbow such that hand ends exactly at target; fail outside reach."""
    dx, dy = target.x - shoulder.x, target.y - shoulder.y
    radius = hypot(dx, dy)
    if radius < EPSILON or radius > upper + lower + EPSILON or radius < abs(upper - lower) - EPSILON:
        raise MotionError("Target outside two-bone reach")
    cos_theta = (upper * upper + radius * radius - lower * lower) / (2 * upper * radius)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    theta = atan2(dy, dx) + bend * acos(cos_theta)
    return Point(x=shoulder.x + upper * cos(theta), y=shoulder.y + upper * sin(theta))


def interpolate(start: Point, end: Point, t: float) -> Point:
    smooth = t * t * (3 - 2 * t)
    return Point(x=start.x + (end.x - start.x) * smooth, y=start.y + (end.y - start.y) * smooth)


def compile_motion(plan: MotionPlan) -> dict:
    """Build one pose per frame with exact prop contact, or reject unsupported sequence."""
    hand = plan.rest_hand
    prop = plan.initial_prop
    held = False
    frames: list[dict] = []
    solve_two_bone(plan.shoulder, hand, plan.upper_arm, plan.forearm, plan.bend)

    for action in plan.actions:
        if action.kind == "grab":
            if held or hypot(hand.x + plan.grip_offset.x - prop.x, hand.y + plan.grip_offset.y - prop.y) > 1.0:
                raise MotionError("Grab requires the prop grip socket to coincide with the wrist")
            held = True
        elif action.kind in ("carry", "place") and not held:
            raise MotionError("Cannot carry/place a prop without grabbing it")
        elif action.kind == "reach" and held:
            raise MotionError("Use carry, not reach, while holding a prop")

        origin = hand
        for frame in range(action.start, action.end + 1):
            if action.kind in MOVE_ACTIONS:
                fraction = (frame - action.start) / (action.end - action.start) if action.end > action.start else 1.0
                hand = interpolate(origin, action.target, fraction)
            elbow = solve_two_bone(plan.shoulder, hand, plan.upper_arm, plan.forearm, plan.bend)
            if held:
                prop = Point(x=hand.x + plan.grip_offset.x,
                             y=hand.y + plan.grip_offset.y)
            if action.kind == "place" and frame == action.end:
                held = False
            frames.append({
                "frame": frame,
                "phase": action.kind,
                "shoulder": plan.shoulder.model_dump(),
                "elbow": elbow.model_dump(),
                "hand": hand.model_dump(),
                "prop": prop.model_dump(),
                "prop_state": "held" if held else "free",
            })

    if held:
        raise MotionError("Shot ends with prop still held; explicit place required")
    return {
        "schema_version": "p4.1",
        "fps": plan.fps,
        "duration_frames": plan.frames,
        "grip_offset": plan.grip_offset.model_dump(),
        "frames": frames,
    }


def compile_file(source: Path, destination: Path) -> Path:
    plan = MotionPlan.model_validate_json(source.read_text(encoding="utf-8"))
    compiled = compile_motion(plan)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(compiled, indent=2), encoding="utf-8")
    return destination
