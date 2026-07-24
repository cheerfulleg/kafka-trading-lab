import json
from functools import lru_cache
from pathlib import Path
from typing import cast

from fastavro import parse_schema


def schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "trade_executed.v1.avsc"


@lru_cache
def trade_schema_text() -> str:
    return schema_path().read_text(encoding="utf-8")


@lru_cache
def parsed_trade_schema() -> dict[str, object]:
    # fastavro returns a mutable schema structure; callers must treat it as read-only.
    return cast(dict[str, object], parse_schema(json.loads(trade_schema_text())))
