from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = re.compile(r"(?:scene_asset|scene_breakdown|beat_timing|prompt_composer|genielabs|feat/p0-p1-foundation)", re.IGNORECASE)
IMPORT_LINE = re.compile(r"^\s*(?:from\s+[\w.]+\s+import|import\s+[\w., ]+|import\s+.*?from\s+['\"]|export\s+.*?from\s+['\"])", re.MULTILINE)


def test_active_python_and_typescript_imports_exclude_legacy_domains():
    violations = []
    for directory in (ROOT / "app", ROOT / "src"):
        for path in directory.rglob("*"):
            if path.suffix not in {".py", ".ts", ".tsx"}:
                continue
            for match in IMPORT_LINE.finditer(path.read_text(encoding="utf-8")):
                if FORBIDDEN.search(match.group(0)):
                    violations.append(f"{path.relative_to(ROOT)}: {match.group(0).strip()}")
    assert violations == []
    for path in (ROOT / "package.json", ROOT / "package-lock.json"):
        if path.exists():
            assert not FORBIDDEN.search(path.read_text(encoding="utf-8")), f"forbidden build dependency in {path.name}"
