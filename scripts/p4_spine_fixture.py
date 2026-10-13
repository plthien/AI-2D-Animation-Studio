"""Create 5-part reference rig via the pinned Genielabs builder and atlas packer.

Purpose: browser-verify that P4 compiled wrist coordinates drive REAL Spine
bone transforms. No Gemini/G-Labs, no fake procedural arm graphics.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from studio.rigging import build_rig_config, run_genielabs_builder


def make_parts(parts: Path, variant: str = "baseline") -> dict:
    parts.mkdir(parents=True, exist_ok=True)
    sizes = {
        "torso": (72, 112),
        "head": (86, 83),
        "upper_arm": (100, 28),
        "forearm": (91, 24),
        "hand": (29, 29),
    }
    mapping = {
        "torso": "torso", "head": "head", "upper_arm": "left_upper_arm",
        "forearm": "left_forearm", "hand": "left_hand",
    }
    positions = {
        "torso": (105, 170), "head": (92, 76), "upper_arm": (136, 152),
        "forearm": (225, 154), "hand": (300, 151),
    }
    if variant == "compact":
        sizes = {
            "torso": (64, 102), "head": (76, 75),
            "upper_arm": (78, 25), "forearm": (70, 23), "hand": (27, 27),
        }
        positions = {
            "torso": (143, 194), "head": (129, 95),
            "upper_arm": (171, 172), "forearm": (239, 174),
            "hand": (298, 171),
        }
    colors = {
        "torso": "#e4a052", "head": "#344c61", "upper_arm": "#405d76",
        "forearm": "#4c728f", "hand": "#344c61",
    }
    reference = Image.new("RGBA", (640, 480), (231, 224, 210, 255))
    draw_ref = ImageDraw.Draw(reference)
    for name in ("torso", "head", "upper_arm", "forearm", "hand"):
        w, h = sizes[name]
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((3, 3, w - 4, h - 4), radius=min(13, h // 3),
                               fill=colors[name], outline="#263747", width=3)
        if name == "head":
            draw.ellipse((24, 28, 31, 37), fill="white")
            draw.ellipse((52, 28, 59, 37), fill="white")
            draw.arc((32, 39, 54, 60), start=0, end=175, fill="white", width=3)
        elif name == "torso":
            for x in (18, 28, 38, 48):
                draw.line((x, 30, x, 72), fill="#b77b43", width=2)
        img.save(parts / f"{name}.png")
        reference.alpha_composite(img, positions[name])
    reference.convert("RGB").save(parts.parent / "character_reference.png")
    return {
        "canvas_width": 640, "canvas_height": 480,
        "parts": {name: {"x": x, "y": y, "width": sizes[name][0],
                         "height": sizes[name][1]}
                  for name, (x, y) in positions.items()},
    }, mapping


def produce(upstream: Path, output: Path, variant: str = "baseline") -> None:
    script = upstream / "scripts" / "make_atlas.py"
    if not script.is_file():
        raise FileNotFoundError(f"Genielabs atlas packer missing: {script}")
    parts = output / "parts"
    layout, semantic = make_parts(parts, variant)
    anchors = {
        "torso": {"x": 140, "y": 210},
        "head": {"x": 135, "y": 110},
        "left_upper_arm": {"x": 140, "y": 165},
        "left_forearm": {"x": 230, "y": 165},
        "left_hand": {"x": 310, "y": 165},
    }
    if variant == "compact":
        anchors = {
            "torso": {"x": 175, "y": 230},
            "head": {"x": 168, "y": 133},
            "left_upper_arm": {"x": 175, "y": 185},
            "left_forearm": {"x": 245, "y": 185},
            "left_hand": {"x": 310, "y": 185},
        }
    upper_length = anchors["left_forearm"]["x"] - anchors["left_upper_arm"]["x"]
    forearm_length = anchors["left_hand"]["x"] - anchors["left_forearm"]["x"]
    config = build_rig_config(layout, semantic, anchors, ["idle", "wave"])
    for bone in config["bones"]:
        if bone["name"] == "left-upper-arm":
            bone["length"] = upper_length
        elif bone["name"] == "left-lower-arm":
            bone["length"] = forearm_length
    output.mkdir(parents=True, exist_ok=True)
    (output / "layout.json").write_text(json.dumps(layout, indent=2))
    (output / "semantic.json").write_text(json.dumps(semantic, indent=2))
    (output / "anchors.json").write_text(json.dumps(anchors, indent=2))
    config_path = output / "rig_config.json"
    config_path.write_text(json.dumps(config, indent=2))
    run_genielabs_builder(upstream, config_path, output / "skeleton.json")
    subprocess.run([sys.executable, str(script), "--parts", str(parts),
                    "--output", str(output), "--name", "skeleton"], check=True)

    skeleton = json.loads((output / "skeleton.json").read_text())
    bones = {b["name"]: b for b in skeleton["bones"]}
    for key in ("torso", "head", "left-upper-arm", "left-lower-arm", "left-hand"):
        if key not in bones:
            raise ValueError(f"Expected multi-part bone missing: {key}")
    if bones["left-lower-arm"]["parent"] != "left-upper-arm" or bones["left-hand"]["parent"] != "left-lower-arm":
        raise ValueError("Incorrect arm chain parentage")
    if bones["left-lower-arm"]["x"] != upper_length or bones["left-hand"]["x"] != forearm_length:
        raise ValueError("Arm chain bone lengths/pivots do not match rig profile")
    profile = {
        "schema_version": "1.0",
        "rig_id": variant,
        "bones": {"upper_arm": "left-upper-arm", "forearm": "left-lower-arm", "hand": "left-hand"},
        "actor_origin": {"x": 320, "y": 480},
        "shoulder": anchors["left_upper_arm"],
        "upper_arm": upper_length,
        "forearm": forearm_length,
        "grip_offset": {"x": -16, "y": 0},
    }
    (output / "rig_profile.json").write_text(json.dumps(profile, indent=2))
    print(f"Genielabs 5-part Spine rig ready: {variant} in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--genielabs", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("outputs/p4_spine_rig"))
    parser.add_argument("--variant", choices=("baseline", "compact"), default="baseline")
    opts = parser.parse_args()
    produce(opts.genielabs, opts.out, opts.variant)
