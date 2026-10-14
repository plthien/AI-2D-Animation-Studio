from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app


def canonical_openapi() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    destination = ROOT / "openapi.json"
    destination.write_text(canonical_openapi(), encoding="utf-8", newline="\n")
    print(f"Wrote {destination}")
