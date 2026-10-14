from __future__ import annotations

from typing import Any

from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from app.core.hashing import canonical_json


class JSONText(TypeDecorator[Any]):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, _dialect: Any) -> str | None:
        return None if value is None else canonical_json(value).decode("utf-8")

    def process_result_value(self, value: str | None, _dialect: Any) -> Any:
        import json
        return None if value is None else json.loads(value)
