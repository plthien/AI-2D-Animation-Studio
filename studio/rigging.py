"""Validated handoff from Genielabs layout to semantic rig configuration.

The Genielabs builder accepts config with bones/slots/attachments, NOT the
position_parts.py layout shape. A caller must supply semantic names and
explicit joint anchors; we do not silently guess pivot positions.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from collections.abc import Mapping

REQUIRED = frozenset({"head", "torso"})
PARENTS = {
    "head": "torso",
    "left_upper_arm": "torso",
    "right_upper_arm": "torso",
    "left_forearm": "left_upper_arm",
    "right_forearm": "right_upper_arm",
    "left_hand": "left_forearm",
    "right_hand": "right_forearm",
    "left_thigh": "torso",
    "right_thigh": "torso",
    "left_shin": "left_thigh",
    "right_shin": "right_thigh",
    "left_foot": "left_shin",
    "right_foot": "right_shin",
}
PRESETS = frozenset({"idle", "walk", "run", "wave", "jump", "attack"})


class RigError(ValueError):
    pass


def build_rig_config(layout: Mapping, semantic_map: Mapping[str, str], joint_anchors: Mapping[str, Mapping[str, float]], animations: list[str]) -> dict:
    """Create Genielabs builder config from explicit semantic mapping and pivots.

    semantic_map maps part file stems from layout['parts'] -> anatomical labels.
    joint_anchors maps anatomical label -> absolute reference-image {x,y}.
    """
    parts = layout.get("parts", {})
    width, height = layout.get("canvas_width"), layout.get("canvas_height")
    if not isinstance(parts, dict) or not parts or not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
        raise RigError("Invalid layout canvas/parts")
    if set(semantic_map) != set(parts):
        raise RigError("Every positioned part must have exactly one semantic mapping")
    labels = list(semantic_map.values())
    if len(set(labels)) != len(labels) or any(label not in (REQUIRED | PARENTS.keys()) for label in labels):
        raise RigError("Duplicate or unknown anatomical label")
    if not REQUIRED.issubset(labels):
        raise RigError("Missing required head/torso")
    if any(parent not in labels for label, parent in PARENTS.items() if label in labels):
        raise RigError("Missing parent part")
    if set(joint_anchors) != set(labels):
        raise RigError("Explicit joint anchor required for every part")
    if any(a not in PRESETS for a in animations):
        raise RigError("Unknown animation preset")

    ordered = [name for name in ("torso", "head", *PARENTS.keys()) if name in labels]
    by_label = {semantic_map[stem]: (stem, part) for stem, part in parts.items()}
    anchors: dict[str, tuple[float, float]] = {}
    for name in ordered:
        xy = joint_anchors[name]
        if not isinstance(xy, Mapping) or not all(isinstance(xy.get(axis), (int, float)) for axis in ("x", "y")):
            raise RigError("Missing or invalid joint coordinates")
        x, y = float(xy["x"]), float(xy["y"])
        if not 0 <= x <= width or not 0 <= y <= height:
            raise RigError("Joint outside reference canvas")
        anchors[name] = x, y

    # Genielabs/Spine y axis points upward. Reference layout uses image pixels (y down).
    bones = [{"name": "root"}]
    slots = []
    attachments = {}
    for name in ordered:
        stem, part = by_label[name]
        if not isinstance(part, Mapping) or not all(isinstance(part.get(k), (int, float)) for k in ("x", "y", "width", "height")):
            raise RigError("Incomplete positioned part")
        px, py = anchors[name]
        parent = PARENTS.get(name, "root")
        base_x, base_y = anchors.get(parent, (width / 2, height))
        bones.append({"name": name.replace("_", "-"), "parent": parent.replace("_", "-"),
                      "x": round(px - base_x, 3), "y": round(base_y - py, 3)})
        slots.append({"name": stem, "bone": name.replace("_", "-"), "attachment": stem})
        w, h = float(part["width"]), float(part["height"])
        if w <= 0 or h <= 0:
            raise RigError("Nonpositive sprite dimensions")
        attachments[stem] = {
            "type": "region",
            "path": stem,
            "width": w, "height": h,
            "x": round(float(part["x"]) + w / 2 - px, 3),
            "y": round(py - (float(part["y"]) + h / 2), 3),
        }
    return {"skeleton": {"name": "auto-rig", "width": width, "height": height},
            "bones": bones, "slots": slots, "attachments": attachments, "animations": animations}


def write_rig_config(layout_path: Path, semantic_path: Path, anchors_path: Path, destination: Path, animations: list[str] | None = None) -> Path:
    data = build_rig_config(json.loads(layout_path.read_text(encoding="utf-8")),
                            json.loads(semantic_path.read_text(encoding="utf-8")),
                            json.loads(anchors_path.read_text(encoding="utf-8")),
                            ["idle", "walk", "run"] if animations is None else animations)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return destination


def run_genielabs_builder(repo_root: Path, rig_config: Path, destination: Path) -> Path:
    """Call pinned local Genielabs script; no Gemini API or remote work."""
    script = repo_root / "scripts" / "build_spine_json.py"
    if not script.is_file() or not rig_config.is_file():
        raise FileNotFoundError("Missing Genielabs script or rig config")
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(script), "--config", str(rig_config), "--output", str(destination)], check=True)
    if not destination.is_file():
        raise RuntimeError("Genielabs exited successfully without skeleton")
    return destination
