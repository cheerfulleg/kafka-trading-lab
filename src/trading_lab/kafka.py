from collections.abc import Callable
from typing import Any

from confluent_kafka import DeserializingConsumer, Producer, SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
from confluent_kafka.serialization import StringDeserializer, StringSerializer

from trading_lab.config import Settings
from trading_lab.models import TradeExecuted
from trading_lab.schema import trade_schema_text


def _to_dict(event: TradeExecuted, _: Any) -> dict[str, object]:
    return event.to_avro_dict()


def _from_dict(
    payload: dict[str, object] | None,
    _: Any,
) -> TradeExecuted | None:
    return TradeExecuted.from_avro_dict(payload) if payload is not None else None


def schema_registry(settings: Settings) -> SchemaRegistryClient:
    return SchemaRegistryClient({"url": settings.schema_registry_url})


def build_trade_producer(settings: Settings) -> SerializingProducer:
    serializer = AvroSerializer(
        schema_registry_client=schema_registry(settings),
        schema_str=trade_schema_text(),
        to_dict=_to_dict,
    )
    return SerializingProducer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer": serializer,
            "enable.idempotence": True,
            "acks": "all",
            "compression.type": "snappy",
        }
    )


def build_trade_consumer(settings: Settings) -> DeserializingConsumer:
    deserializer = AvroDeserializer(
        schema_registry_client=schema_registry(settings),
        schema_str=trade_schema_text(),
        from_dict=_from_dict,
    )
    return DeserializingConsumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.trade_consumer_group,
            "key.deserializer": StringDeserializer("utf_8"),
            "value.deserializer": deserializer,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def build_dead_letter_producer(settings: Settings) -> Producer:
    """Build a producer that preserves malformed records without decoding them."""

    return Producer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "enable.idempotence": True,
            "acks": "all",
            "compression.type": "snappy",
        }
    )


DeliveryCallback = Callable[[object, object], None]
