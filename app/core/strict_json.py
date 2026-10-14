from __future__ import annotations

import json
from typing import Any


class DuplicateJSONKey(ValueError):
    pass


def _object_from_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKey(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def strict_json_loads(value: str | bytes) -> Any:
    return json.loads(value, object_pairs_hook=_object_from_pairs, parse_constant=_reject_constant)
