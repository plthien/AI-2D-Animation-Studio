"""Execute FilmPlan v2 locally with supplied rig/PNG assets and narration WAV files.

No AI APIs; requires installed Node runtime, Playwright Chromium and FFmpeg.
The assets must exist under runtime/fixtures according to the AssetCatalog.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from prepare_film_v2 import prepare
from studio.film_v2 import AssetCatalog, FilmPlanV2
from studio.voice import assemble_file


def run(plan: Path, catalog: Path, motions: Path, voices: Path,
        output: Path, workspace: Path | None = None) -> None:
    root=Path(__file__).resolve().parents[1]
    fixtures=root/"runtime"/"fixtures"
    assets=AssetCatalog.model_validate_json(catalog.read_text(encoding="utf-8"))
    film=FilmPlanV2.model_validate_json(plan.read_text(encoding="utf-8"))
    for value in assets.rigs.values():
        path=fixtures/value.directory
        for name in ("skeleton.json","skeleton.atlas","skeleton.png","rig_profile.json"):
            if not (path/name).is_file():
                raise FileNotFoundError(f"Missing Spine rig asset: {path/name}")
    for value in (*assets.backgrounds.values(), *assets.props.values()):
        if not (fixtures/value.image).is_file():
            raise FileNotFoundError(f"Missing PNG image: {fixtures/value.image}")
    for shot in film.shots:
        if shot.narration is not None and not (voices/shot.narration.wav).is_file():
            raise FileNotFoundError(f"Missing voice for shot {shot.shot_id}")
    prepare(plan,catalog,motions,fixtures)
    temp=workspace.resolve() if workspace is not None else root/"outputs"/"p6_v2"
    temp.mkdir(parents=True,exist_ok=True)
    # Shorter subsequent films must never inherit frames from previous renders.
    shutil.rmtree(temp/"frames",ignore_errors=True)
    shutil.rmtree(temp/"previews",ignore_errors=True)
    assemble_file(fixtures/"film_timeline.json",voices,temp/"narration.wav",
                  temp/"audio_manifest.json")
    subprocess.run(["npm","run","build:film-v2"],cwd=root/"runtime",check=True)
    subprocess.run(["node","runtime/film_v2_render.mjs",str(temp)],cwd=root,check=True)
    output=output.resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-framerate",str(film.fps),"-i",str(temp/"frames"/"frame_%06d.png"),
        "-i",str(temp/"narration.wav"),"-map","0:v:0","-map","1:a:0",
        "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",
        "-b:a","96k",str(output),
    ],cwd=root,check=True)
    movie=json.loads(subprocess.check_output([
        "ffprobe","-v","error","-count_frames",
        "-show_entries","format=duration:stream=codec_type,nb_read_frames",
        "-of","json",str(output)],text=True))
    video=next((s for s in movie["streams"] if s.get("codec_type")=="video"),None)
    expected=sum(s.duration_frames for s in film.shots)
    if video is None or int(video.get("nb_read_frames",0))!=expected:
        raise RuntimeError("Final MP4 video frame count mismatch")
    print(f"Film ready: {output} ({expected} frames, {len(film.shots)} independently authored shots)")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Compile + render film.v2 from existing assets and WAVs")
    parser.add_argument("--plan",type=Path,required=True)
    parser.add_argument("--catalog",type=Path,required=True)
    parser.add_argument("--motions",type=Path,required=True)
    parser.add_argument("--voices",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--workspace",type=Path,default=None,
                        help="Dedicated intermediate frame/audio directory per film")
    args=parser.parse_args()
    run(args.plan,args.catalog,args.motions,args.voices,args.output,args.workspace)
