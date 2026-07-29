import pytest

from confluent_kafka import KafkaException

from trading_lab.dead_letter import dead_letter_headers, route_to_dead_letter


class FakeMessage:
    def topic(self) -> str:
        return "trades.v1"

    def partition(self) -> int:
        return 2

    def offset(self) -> int:
        return 41

    def key(self) -> bytes:
        return b"AAPL"

    def value(self) -> bytes:
        return b"not-avro"


class FakeProducer:
    def __init__(self, remaining: int = 0) -> None:
        self.remaining = remaining
        self.produced: dict[str, object] | None = None
        self.flush_timeout: int | None = None

    def produce(self, **kwargs: object) -> None:
        self.produced = kwargs

    def flush(self, timeout: int) -> int:
        self.flush_timeout = timeout
        return self.remaining


def test_dead_letter_headers_include_origin_and_error_metadata() -> None:
    headers = dict(
        dead_letter_headers(  # type: ignore[arg-type]
            FakeMessage(), ValueError("invalid payload")
        )
    )

    assert headers["x-original-topic"] == "trades.v1"
    assert headers["x-original-partition"] == "2"
    assert headers["x-original-offset"] == "41"
    assert headers["x-error-type"] == "ValueError"
    assert headers["x-error-message"] == "invalid payload"
    assert headers["x-failed-at"].endswith("+00:00")


def test_route_to_dead_letter_preserves_raw_record_after_flush() -> None:
    producer = FakeProducer()

    route_to_dead_letter(  # type: ignore[arg-type]
        producer, "trades.v1.dlq", FakeMessage(), ValueError("bad")
    )

    assert producer.produced is not None
    assert producer.produced["topic"] == "trades.v1.dlq"
    assert producer.produced["key"] == b"AAPL"
    assert producer.produced["value"] == b"not-avro"
    assert producer.flush_timeout == 10


def test_route_to_dead_letter_raises_when_delivery_does_not_complete() -> None:
    with pytest.raises(KafkaException, match="not delivered"):
        route_to_dead_letter(
            FakeProducer(remaining=1),  # type: ignore[arg-type]
            "trades.v1.dlq",
            FakeMessage(),  # type: ignore[arg-type]
            ValueError("bad"),
        )
