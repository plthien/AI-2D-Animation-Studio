"""Compile the same manual director plan for a real Spine rig and shared world object."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from studio.motion import MotionPlan
from studio.retarget import RigProfile
from studio.world import WorldProp, compile_world_motion

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("motion",type=Path)
    parser.add_argument("profile",type=Path)
    parser.add_argument("skeleton",type=Path)
    parser.add_argument("world_prop",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    result=compile_world_motion(
        MotionPlan.model_validate_json(args.motion.read_text(encoding="utf-8")),
        RigProfile.model_validate_json(args.profile.read_text(encoding="utf-8")),
        json.loads(args.skeleton.read_text(encoding="utf-8")),
        WorldProp.model_validate_json(args.world_prop.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print("World contact compiled:",args.output)
