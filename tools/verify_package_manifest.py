"""Verify immutable specification snapshot entries, not the entire Git checkout.

The manifest enumerates approved spec files at publication time. A real repository
also contains .git, newly implemented runtime code, test caches and P0 QA outputs.
Those files are intentionally not part of this immutable snapshot.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def verify(root: Path = ROOT) -> int:
    root = root.resolve()
    manifest = json.loads((root / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    entries = manifest["files"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("Manifest must contain nonempty files list")
    if manifest.get("file_count") != len(entries):
        raise ValueError("Manifest file_count disagrees with files list")

    seen: set[str] = set()
    for entry in entries:
        name = entry["path"]
        if not isinstance(name, str) or not name or "\\" in name:
            raise ValueError(f"Invalid manifest path: {name!r}")
        posix = PurePosixPath(name)
        if posix.is_absolute() or any(part in {"", ".", ".."} for part in name.split("/")):
            raise ValueError(f"Unsafe manifest path: {name!r}")
        if name == "PACKAGE_MANIFEST.json":
            raise ValueError("Self-referential manifest entry is forbidden")
        if name in seen:
            raise ValueError(f"Duplicate manifest path: {name}")
        seen.add(name)
        target = root.joinpath(*posix.parts)
        if target.is_symlink() or not target.is_file():
            raise ValueError(f"Manifest file missing or symlinked: {name}")
        content = target.read_bytes()
        if len(content) != entry["bytes"]:
            raise ValueError(f"Manifest size mismatch: {name}")
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise ValueError(f"Manifest SHA256 mismatch: {name}")
    return len(seen)


def main() -> None:
    print(f"PASS manifest integrity {verify()} registered specification files")


if __name__ == "__main__":
    main()
