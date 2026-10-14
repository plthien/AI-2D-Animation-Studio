from __future__ import annotations

from uuid import uuid4


def new_id(prefix: str) -> str:
    allowed = {"chn", "prj", "art", "ast", "av", "rig", "rv", "mot", "mv", "op", "job", "res"}
    if prefix not in allowed:
        raise ValueError("unsupported ID prefix")
    return f"{prefix}_{uuid4().hex}"
