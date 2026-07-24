import argparse
import logging
import random
from decimal import Decimal
from uuid import uuid4

from confluent_kafka import KafkaError, KafkaException, Message

from trading_lab.config import get_settings
from trading_lab.kafka import build_trade_producer
from trading_lab.models import TradeExecuted, TradeSide

logger = logging.getLogger(__name__)


def sample_trade() -> TradeExecuted:
    symbol = random.choice(("AAPL", "MSFT", "NVDA", "TSLA"))
    return TradeExecuted(
        trade_id=f"TRD-{uuid4().hex[:12].upper()}",
        account_id=f"ACC-{random.randint(1, 20):04d}",
        symbol=symbol,
        side=random.choice(tuple(TradeSide)),
        quantity=Decimal(random.randint(1, 100)),
        price=Decimal(random.randint(10_000, 50_000)) / 100,
    )


def delivery_report(error: KafkaError | None, message: Message) -> None:
    if error is not None:
        logger.error("trade delivery failed: %s", error)
        return
    logger.info(
        "trade delivered topic=%s partition=%s offset=%s",
        message.topic(),
        message.partition(),
        message.offset(),
    )


def produce(count: int) -> None:
    settings = get_settings()
    producer = build_trade_producer(settings)

    for _ in range(count):
        trade = sample_trade()
        producer.produce(
            topic=settings.trade_topic,
            key=trade.symbol,
            value=trade,
            on_delivery=delivery_report,
        )
        producer.poll(0)

    remaining = producer.flush(10)
    if remaining:
        raise KafkaException(f"{remaining} message(s) were not delivered")


def main() -> None:
    parser = argparse.ArgumentParser(description="Produce sample trade events")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be positive")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    produce(args.count)


if __name__ == "__main__":
    main()
