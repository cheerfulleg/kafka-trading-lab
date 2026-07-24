from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO

from fastavro import schemaless_reader, schemaless_writer

from trading_lab.models import (
    MarketPriceUpdated,
    OrderPlaced,
    OrderType,
    TradeExecuted,
    TradeSide,
)
from trading_lab.schema import (
    parsed_market_price_schema,
    parsed_order_schema,
    parsed_trade_schema,
)


def test_market_price_avro_round_trip() -> None:
    price = MarketPriceUpdated(
        symbol="MSFT",
        price=Decimal("440.10"),
        currency="USD",
        source="NASDAQ",
        updated_at=datetime(2026, 7, 25, 15, 30, tzinfo=UTC),
    )
    buffer = BytesIO()

    schemaless_writer(buffer, parsed_market_price_schema(), price.to_avro_dict())
    buffer.seek(0)
    decoded = schemaless_reader(buffer, parsed_market_price_schema())
    restored = MarketPriceUpdated.from_avro_dict(decoded)

    assert restored == price
    assert restored.partition_key() == "MSFT"


def test_order_avro_round_trip() -> None:
    order = OrderPlaced(
        order_id="ORD-ROUNDTRIP",
        account_id="ACC-007",
        symbol="MSFT",
        side=TradeSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("4.25"),
        limit_price=Decimal("440.10"),
        placed_at=datetime(2026, 7, 25, 15, 30, tzinfo=UTC),
    )
    buffer = BytesIO()

    schemaless_writer(buffer, parsed_order_schema(), order.to_avro_dict())
    buffer.seek(0)
    decoded = schemaless_reader(buffer, parsed_order_schema())
    restored = OrderPlaced.from_avro_dict(decoded)

    assert restored == order


def test_market_order_avro_round_trip_preserves_null_price() -> None:
    order = OrderPlaced(
        order_id="ORD-MARKET",
        account_id="ACC-008",
        symbol="NVDA",
        side=TradeSide.SELL,
        order_type=OrderType.MARKET,
        quantity=Decimal("2"),
        placed_at=datetime(2026, 7, 25, 15, 30, tzinfo=UTC),
    )
    buffer = BytesIO()

    schemaless_writer(buffer, parsed_order_schema(), order.to_avro_dict())
    buffer.seek(0)
    decoded = schemaless_reader(buffer, parsed_order_schema())

    assert decoded["limit_price"] is None
    assert OrderPlaced.from_avro_dict(decoded) == order


def test_trade_avro_round_trip() -> None:
    trade = TradeExecuted(
        trade_id="TRD-ROUNDTRIP",
        account_id="ACC-007",
        symbol="MSFT",
        side=TradeSide.SELL,
        quantity=Decimal("4.25"),
        price=Decimal("440.10"),
        executed_at=datetime(2026, 7, 24, 15, 30, tzinfo=UTC),
    )
    buffer = BytesIO()

    schemaless_writer(buffer, parsed_trade_schema(), trade.to_avro_dict())
    buffer.seek(0)
    decoded = schemaless_reader(buffer, parsed_trade_schema())
    restored = TradeExecuted.from_avro_dict(decoded)

    assert restored == trade
