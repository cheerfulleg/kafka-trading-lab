from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)


class TradeSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderPlaced(BaseModel):
    """Application representation of the version-one order event."""

    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    order_id: str = Field(min_length=1, max_length=64)
    account_id: str = Field(min_length=1, max_length=64)
    symbol: str = Field(min_length=1, max_length=16)
    side: TradeSide
    order_type: OrderType
    quantity: Decimal = Field(gt=0)
    limit_price: Decimal | None = Field(default=None, gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    placed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("symbol", "currency")
    @classmethod
    def uppercase_market_fields(cls, value: str) -> str:
        return value.upper()

    @field_validator("placed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("placed_at must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def validate_limit_price(self) -> "OrderPlaced":
        if self.order_type is OrderType.LIMIT and self.limit_price is None:
            raise ValueError("limit_price is required for LIMIT orders")
        if self.order_type is OrderType.MARKET and self.limit_price is not None:
            raise ValueError("limit_price must be absent for MARKET orders")
        return self

    @field_serializer("event_id")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)

    @field_serializer("quantity", "limit_price")
    def serialize_decimal(self, value: Decimal | None) -> str | None:
        return format(value, "f") if value is not None else None

    @field_serializer("placed_at")
    def serialize_datetime(self, value: datetime) -> int:
        return int(value.timestamp() * 1000)

    def to_avro_dict(self) -> dict[str, object]:
        """Return values matching the public Avro contract."""

        return self.model_dump(mode="json")

    @classmethod
    def from_avro_dict(cls, payload: dict[str, object]) -> "OrderPlaced":
        """Validate and convert a decoded Avro record."""

        return cls.model_validate(payload)


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
