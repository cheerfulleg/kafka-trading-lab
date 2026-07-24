from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading_lab.models import (
    MarketPriceUpdated,
    OrderPlaced,
    OrderType,
    TradeExecuted,
    TradeSide,
)


def test_market_price_normalizes_key_and_serializes_for_avro() -> None:
    price = MarketPriceUpdated(
        symbol="aapl",
        price=Decimal("189.2500"),
        currency="usd",
        source="NASDAQ",
        updated_at=datetime(2026, 7, 25, 12, 0, tzinfo=UTC),
    )

    payload = price.to_avro_dict()

    assert price.partition_key() == "AAPL"
    assert payload["symbol"] == price.partition_key()
    assert payload["price"] == "189.2500"
    assert payload["currency"] == "USD"
    assert payload["updated_at"] == int(price.updated_at.timestamp() * 1000)


def test_market_price_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        MarketPriceUpdated(
            symbol="AAPL",
            price=Decimal("189.25"),
            source="NASDAQ",
            updated_at=datetime(2026, 7, 25, 12, 0),
        )


def test_market_price_rejects_non_positive_price() -> None:
    with pytest.raises(ValidationError):
        MarketPriceUpdated(
            symbol="AAPL",
            price=Decimal("0"),
            source="NASDAQ",
        )


def test_limit_order_normalizes_and_serializes_for_avro() -> None:
    order = OrderPlaced(
        order_id="ORD-001",
        account_id="ACC-001",
        symbol="aapl",
        side=TradeSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("10.50"),
        limit_price=Decimal("189.25"),
        currency="usd",
        placed_at=datetime(2026, 7, 25, 12, 0, tzinfo=UTC),
    )

    payload = order.to_avro_dict()

    assert order.symbol == "AAPL"
    assert payload["quantity"] == "10.50"
    assert payload["limit_price"] == "189.25"
    assert payload["currency"] == "USD"
    assert payload["placed_at"] == int(order.placed_at.timestamp() * 1000)


@pytest.mark.parametrize(
    ("order_type", "limit_price", "message"),
    (
        (OrderType.LIMIT, None, "required for LIMIT"),
        (OrderType.MARKET, Decimal("100"), "absent for MARKET"),
    ),
)
def test_order_enforces_price_semantics(
    order_type: OrderType,
    limit_price: Decimal | None,
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        OrderPlaced(
            order_id="ORD-001",
            account_id="ACC-001",
            symbol="AAPL",
            side=TradeSide.BUY,
            order_type=order_type,
            quantity=Decimal("1"),
            limit_price=limit_price,
        )


def test_order_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        OrderPlaced(
            order_id="ORD-001",
            account_id="ACC-001",
            symbol="AAPL",
            side=TradeSide.SELL,
            order_type=OrderType.MARKET,
            quantity=Decimal("1"),
            placed_at=datetime(2026, 7, 25, 12, 0),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (("quantity", "0"), ("limit_price", "-1")),
)
def test_order_rejects_non_positive_numbers(field: str, value: str) -> None:
    payload = {
        "order_id": "ORD-001",
        "account_id": "ACC-001",
        "symbol": "AAPL",
        "side": TradeSide.BUY,
        "order_type": OrderType.LIMIT,
        "quantity": Decimal("1"),
        "limit_price": Decimal("100"),
    }
    payload[field] = Decimal(value)

    with pytest.raises(ValidationError):
        OrderPlaced.model_validate(payload)


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
