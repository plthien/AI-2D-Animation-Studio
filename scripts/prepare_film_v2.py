"""Compile independent motion plans, then bind per-shot assets in a film.v2 timeline."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from studio.motion import MotionPlan, compile_motion
from studio.film_v2 import FilmPlanV2, AssetCatalog, compile_film_v2


def prepare(plan_file: Path, catalog_file: Path, motion_file: Path, output_root: Path) -> None:
    film=FilmPlanV2.model_validate_json(plan_file.read_text(encoding="utf-8"))
    catalog=AssetCatalog.model_validate_json(catalog_file.read_text(encoding="utf-8"))
    definitions=json.loads(motion_file.read_text(encoding="utf-8"))
    actors = {}
    for shot in film.shots:
        for actor in shot.actors:
            existing=actors.get(actor.motion_id)
            if existing is not None and existing != actor.rig_id:
                raise ValueError("Motion identifier reused with a different rig")
            actors[actor.motion_id] = actor.rig_id
    if set(definitions) != set(actors):
        raise ValueError("All film motion clips must be supplied exactly once")
    clips={}
    for motion_id,rig_id in actors.items():
        clip=compile_motion(MotionPlan.model_validate(definitions[motion_id]))
        clip["rig_id"]=rig_id
        clips[motion_id]=clip
    compiled=compile_film_v2(film,catalog,clips)
    output_root.mkdir(parents=True,exist_ok=True)
    (output_root/"film_timeline.json").write_text(json.dumps(compiled,indent=2),encoding="utf-8")
    (output_root/"film_motions.json").write_text(json.dumps(clips,indent=2),encoding="utf-8")
    print(f"Prepared {len(film.shots)} independent shots, {len(clips)} motions, "
          f"{compiled['total_frames']} frames")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("plan",type=Path)
    parser.add_argument("catalog",type=Path)
    parser.add_argument("motions",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    prepare(args.plan,args.catalog,args.motions,args.output)
