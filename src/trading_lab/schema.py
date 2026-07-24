import json
from functools import lru_cache
from pathlib import Path
from typing import cast

from fastavro import parse_schema


def trade_schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "trade_executed.v1.avsc"


def schema_path() -> Path:
    """Return the trade schema path retained for backward compatibility."""

    return trade_schema_path()


def order_schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "order_placed.v1.avsc"


def market_price_schema_path() -> Path:
    return (
        Path(__file__).resolve().parents[2] / "schemas" / "market_price_updated.v1.avsc"
    )


@lru_cache
def trade_schema_text() -> str:
    return trade_schema_path().read_text(encoding="utf-8")


@lru_cache
def order_schema_text() -> str:
    return order_schema_path().read_text(encoding="utf-8")


@lru_cache
def market_price_schema_text() -> str:
    return market_price_schema_path().read_text(encoding="utf-8")


@lru_cache
def parsed_trade_schema() -> dict[str, object]:
    # fastavro returns a mutable schema structure; callers must treat it as read-only.
    return cast(dict[str, object], parse_schema(json.loads(trade_schema_text())))


@lru_cache
def parsed_order_schema() -> dict[str, object]:
    # fastavro returns a mutable schema structure; callers must treat it as read-only.
    return cast(dict[str, object], parse_schema(json.loads(order_schema_text())))


@lru_cache
def parsed_market_price_schema() -> dict[str, object]:
    # fastavro returns a mutable schema structure; callers must treat it as read-only.
    return cast(dict[str, object], parse_schema(json.loads(market_price_schema_text())))
