"""Shared world-space prop targets and orientation-aware hand contact.

The SAME world prop start/place coordinates are used for every rig. Unlike the
actor-local P4.2 mode this code never scales, translates or restages the object.
Only the actor's rest wrist is remapped; scripted carry target is a world point.
"""
from __future__ import annotations

from math import cos, radians, sin

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from studio.motion import MotionAction, MotionError, MotionPlan, Point, compile_motion, interpolate
from studio.retarget import RigProfile, validate_spine_profile


class WorldProp(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prop_id: str = Field(min_length=1)
    initial: Point
    destination: Point
    grip_offset: Point
    initial_angle_deg: FiniteFloat = 0.0
    carry_angle_deg: FiniteFloat = 0.0
    final_angle_deg: FiniteFloat = 0.0


def socket_offset(offset: Point, angle: float) -> Point:
    """Prop center relative to wrist; rotate the prop's *local* grip vector."""
    theta = radians(angle)
    return Point(x=offset.x * cos(theta) - offset.y * sin(theta),
                 y=offset.x * sin(theta) + offset.y * cos(theta))


def wrist_for_prop(center: Point, offset: Point, angle: float) -> Point:
    rotated = socket_offset(offset, angle)
    return Point(x=center.x - rotated.x, y=center.y - rotated.y)


def compile_world_motion(source: MotionPlan, profile: RigProfile, skeleton: dict,
                         prop: WorldProp) -> dict:
    """One action plan, same world anchors, two arm lengths; fail closed on reach."""
    validate_spine_profile(profile, skeleton)
    kinds = [a.kind for a in source.actions]
    if kinds.count("reach") != 1 or kinds.count("grab") != 1 or kinds.count("place") != 1 or kinds[-1] != "place":
        raise MotionError("World contact requires one reach, grab, final place")
    if not (kinds.index("reach") < kinds.index("grab") < kinds.index("place")):
        raise MotionError("World contact action order invalid")
    if any(k not in ("reach", "grab", "carry", "wait", "place") for k in kinds):
        raise MotionError("Unsupported world contact action")

    ratio = (profile.upper_arm + profile.forearm) / (source.upper_arm + source.forearm)
    rest = Point(x=profile.shoulder.x + (source.rest_hand.x - source.shoulder.x) * ratio,
                 y=profile.shoulder.y + (source.rest_hand.y - source.shoulder.y) * ratio)
    initial_wrist = wrist_for_prop(prop.initial, prop.grip_offset, prop.initial_angle_deg)
    final_wrist = wrist_for_prop(prop.destination, prop.grip_offset, prop.final_angle_deg)
    # Carry's source coordinates are absolute world waypoints, deliberately unscaled.
    actions = [a.model_copy(update={"target": initial_wrist}) if a.kind == "reach"
               else a.model_copy(update={"target": final_wrist}) if a.kind == "place"
               else a for a in source.actions]
    # IK + grab/place state machine already tested in MotionCompiler: use a zero
    # socket for wrist path and apply the rotated physical socket afterwards.
    zero = Point(x=0, y=0)
    plan = source.model_copy(update={
        "shoulder": profile.shoulder,
        "rest_hand": rest,
        "upper_arm": profile.upper_arm,
        "forearm": profile.forearm,
        "initial_prop": initial_wrist,
        "grip_offset": zero,
        "actions": actions,
    })
    result = compile_motion(plan)
    current_angle = prop.initial_angle_deg
    carried = False
    for action in actions:
        origin = current_angle
        destination = (prop.carry_angle_deg if action.kind == "carry"
                       else prop.final_angle_deg if action.kind == "place"
                       else origin)
        for frame in range(action.start, action.end + 1):
            pose = result["frames"][frame]
            t = (frame - action.start) / (action.end - action.start) if action.end > action.start else 1.0
            angle = origin + (destination - origin) * (t*t*(3-2*t))
            offset = socket_offset(prop.grip_offset, angle)
            active = carried or action.kind in ("grab", "carry", "place")
            if active:
                pose["prop"] = {"x": pose["hand"]["x"] + offset.x,
                                "y": pose["hand"]["y"] + offset.y}
            else:
                pose["prop"] = prop.initial.model_dump()
            pose["prop_rotation_deg"] = angle
        if action.kind == "grab":
            carried = True
        elif action.kind == "place":
            carried = False
        current_angle = destination
    # End state must be exactly the same world destination for all rig variants.
    last = result["frames"][-1]["prop"]
    if abs(last["x"] - prop.destination.x) > 0.001 or abs(last["y"] - prop.destination.y) > 0.001:
        raise MotionError("Released prop does not land at fixed world destination")
    result["grip_offset"] = prop.grip_offset.model_dump()
    result["rig"] = profile.model_dump()
    result["world"] = prop.model_dump()
    result["retarget"] = {"mode": "world_fixed_prop", "reach_scale": ratio}
    return result
