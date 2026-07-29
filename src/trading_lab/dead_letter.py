from datetime import UTC, datetime

from confluent_kafka import KafkaException, Message, Producer


def dead_letter_headers(message: Message, error: BaseException) -> list[tuple[str, str]]:
    """Return diagnostic headers without exposing the malformed payload in logs."""

    return [
        ("x-original-topic", message.topic()),
        ("x-original-partition", str(message.partition())),
        ("x-original-offset", str(message.offset())),
        ("x-error-type", type(error).__name__),
        ("x-error-message", str(error)[:512]),
        ("x-failed-at", datetime.now(UTC).isoformat()),
    ]


def route_to_dead_letter(
    producer: Producer,
    topic: str,
    message: Message,
    error: BaseException,
) -> None:
    """Publish the original bytes to the DLQ and wait for broker acknowledgement."""

    producer.produce(
        topic=topic,
        key=message.key(),
        value=message.value(),
        headers=dead_letter_headers(message, error),
    )
    remaining = producer.flush(10)
    if remaining:
        raise KafkaException(f"{remaining} dead-letter message(s) were not delivered")
