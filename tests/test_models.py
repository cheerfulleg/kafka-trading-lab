from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading_lab.models import TradeExecuted, TradeSide


def test_trade_normalizes_market_fields_and_serializes_for_avro() -> None:
    trade = TradeExecuted(
        trade_id="TRD-001",
        account_id="ACC-001",
        symbol="aapl",
        side=TradeSide.BUY,
        quantity=Decimal("10.50"),
        price=Decimal("189.25"),
        currency="usd",
        executed_at=datetime(2026, 7, 24, 12, 0, tzinfo=UTC),
    )

    payload = trade.to_avro_dict()

    assert trade.symbol == "AAPL"
    assert payload["quantity"] == "10.50"
    assert payload["price"] == "189.25"
    assert payload["currency"] == "USD"
    assert payload["executed_at"] == int(trade.executed_at.timestamp() * 1000)


def test_trade_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        TradeExecuted(
            trade_id="TRD-001",
            account_id="ACC-001",
            symbol="AAPL",
            side=TradeSide.SELL,
            quantity=Decimal("1"),
            price=Decimal("100"),
            executed_at=datetime(2026, 7, 24, 12, 0),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (("quantity", "0"), ("price", "-1")),
)
def test_trade_rejects_non_positive_numbers(field: str, value: str) -> None:
    payload = {
        "trade_id": "TRD-001",
        "account_id": "ACC-001",
        "symbol": "AAPL",
        "side": TradeSide.BUY,
        "quantity": Decimal("1"),
        "price": Decimal("100"),
    }
    payload[field] = Decimal(value)

    with pytest.raises(ValidationError):
        TradeExecuted.model_validate(payload)
