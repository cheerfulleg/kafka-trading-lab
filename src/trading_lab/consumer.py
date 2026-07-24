import logging
import signal
from types import FrameType
from typing import cast

from confluent_kafka import KafkaError

from trading_lab.config import get_settings
from trading_lab.kafka import build_trade_consumer
from trading_lab.models import TradeExecuted

logger = logging.getLogger(__name__)


class Shutdown:
    requested = False

    def request(self, _: int, __: FrameType | None) -> None:
        self.requested = True


def consume() -> None:
    settings = get_settings()
    consumer = build_trade_consumer(settings)
    shutdown = Shutdown()
    signal.signal(signal.SIGINT, shutdown.request)
    signal.signal(signal.SIGTERM, shutdown.request)
    consumer.subscribe([settings.trade_topic])

    try:
        while not shutdown.requested:
            message = consumer.poll(1.0)
            if message is None:
                continue
            error = message.error()
            if error is not None:
                if error.code() == KafkaError._PARTITION_EOF:
                    continue
                raise RuntimeError(error)

            trade = cast(TradeExecuted, message.value())
            logger.info(
                "trade consumed trade_id=%s symbol=%s partition=%s offset=%s",
                trade.trade_id,
                trade.symbol,
                message.partition(),
                message.offset(),
            )
            consumer.commit(message=message, asynchronous=False)
    finally:
        consumer.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    consume()


if __name__ == "__main__":
    main()
