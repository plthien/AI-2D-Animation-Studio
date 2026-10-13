"""Run real upstream Genielabs preparation without calling Gemini/LLM APIs.

Stage 1: atlas -> parts. Stage 2: parts+reference -> layout.
Stage 3: approved semantic labels+joint anchors -> rig -> Spine JSON+Atlas.
Uses a separate pinned upstream checkout at --genielabs. Each stage is repeatable.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from studio.rigging import write_rig_config, run_genielabs_builder

def launch(script: Path, *args: str) -> None:
    if not script.is_file():
        raise FileNotFoundError(str(script))
    subprocess.run([sys.executable,str(script),*args],check=True)

def segment(upstream: Path, atlas: Path, parts_dir: Path) -> list[Path]:
    source=upstream/"scripts"/"split_character.py"
    if not source.is_file() or not atlas.is_file():
        raise FileNotFoundError("Missing Genielabs segmenter or atlas")
    spec=importlib.util.spec_from_file_location("genielabs_split_character",source)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [Path(p) for p in module.segment_parts(str(atlas),str(parts_dir))]

def run(args: argparse.Namespace) -> None:
    upstream=Path(args.genielabs).resolve()
    workspace=Path(args.workspace).resolve()
    workspace.mkdir(parents=True,exist_ok=True)
    atlas=Path(args.atlas).resolve()
    reference=Path(args.reference).resolve()
    parts=workspace/"parts"
    layout=workspace/"layout.json"
    config=workspace/"rig_config.json"
    if args.from_stage<=1<=args.through_stage:
        produced=segment(upstream,atlas,parts)
        if not produced:
            raise ValueError("No parts segmented; inspect atlas background/threshold")
        print("PARTS:",len(produced))
    if args.from_stage<=2<=args.through_stage:
        launch(upstream/"scripts"/"position_parts.py","--reference",str(reference),
               "--parts",str(parts),"--output",str(layout),
               "--debug",str(workspace/"debug"))
    if args.from_stage<=3<=args.through_stage:
        for file in (layout,Path(args.semantic),Path(args.anchors)):
            if not file.is_file():
                raise FileNotFoundError(f"Missing approved part mapping or anchor file: {file}")
        write_rig_config(layout,Path(args.semantic),Path(args.anchors),config,
                         ["idle","walk","run"])
        run_genielabs_builder(upstream,config,workspace/"skeleton.json")
        launch(upstream/"scripts"/"make_atlas.py","--parts",str(parts),
               "--output",str(workspace),"--name","skeleton")
        skeleton=json.loads((workspace/"skeleton.json").read_text(encoding="utf-8"))
        expected={s["attachment"] for s in skeleton["slots"]}
        real={p.stem for p in parts.glob("*.png")}
        if expected!=real:
            raise ValueError(f"Attachment vs atlas mismatch: {expected ^ real}")
        print("RIG PACKAGE:",workspace,"animations:",list(skeleton.get("animations",{})))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Offline G-Labs atlas -> Genielabs rig pipeline")
    parser.add_argument("--genielabs",required=True)
    parser.add_argument("--atlas",required=True)
    parser.add_argument("--reference",required=True)
    parser.add_argument("--workspace",required=True)
    parser.add_argument("--semantic",required=True,help="JSON part stem -> anatomical label")
    parser.add_argument("--anchors",required=True,help="JSON anatomical label -> {x,y} reference pixel")
    parser.add_argument("--from-stage",type=int,choices=(1,2,3),default=1)
    parser.add_argument("--through-stage",type=int,choices=(1,2,3),default=3)
    opts=parser.parse_args()
    if opts.from_stage>opts.through_stage:
        parser.error("--from-stage must not exceed --through-stage")
    run(opts)
