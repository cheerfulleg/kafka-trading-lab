from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO

from fastavro import schemaless_reader, schemaless_writer

from trading_lab.models import TradeExecuted, TradeSide
from trading_lab.schema import parsed_trade_schema


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
