from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class TradeSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class TradeExecuted(BaseModel):
    """Application representation of the version-one trade event."""

    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    trade_id: str = Field(min_length=1, max_length=64)
    account_id: str = Field(min_length=1, max_length=64)
    symbol: str = Field(min_length=1, max_length=16)
    side: TradeSide
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("symbol", "currency")
    @classmethod
    def uppercase_market_fields(cls, value: str) -> str:
        return value.upper()

    @field_validator("executed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("executed_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_serializer("event_id")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)

    @field_serializer("quantity", "price")
    def serialize_decimal(self, value: Decimal) -> str:
        return format(value, "f")

    @field_serializer("executed_at")
    def serialize_datetime(self, value: datetime) -> int:
        return int(value.timestamp() * 1000)

    def to_avro_dict(self) -> dict[str, object]:
        """Return values matching the public Avro contract."""

        return self.model_dump(mode="json")

    @classmethod
    def from_avro_dict(cls, payload: dict[str, object]) -> "TradeExecuted":
        """Validate and convert a decoded Avro record."""

        return cls.model_validate(payload)
