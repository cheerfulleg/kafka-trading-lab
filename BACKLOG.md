# Engineering backlog

The autonomous agent selects exactly one unchecked item from the first
non-empty section. Each item should fit in one reviewable pull request.

## Now

- [x] Add an Avro `OrderPlaced` event with validation and round-trip tests.
- [x] Add an Avro `MarketPriceUpdated` event keyed by instrument symbol.
- [ ] Route malformed trade payloads to a dead-letter topic with error metadata.
- [ ] Add deterministic trade IDs and demonstrate idempotent consumer handling.
- [ ] Add a schema compatibility script and document backward-compatible change.

## Next

- [ ] Add a PostgreSQL trade sink with an idempotent upsert.
- [ ] Add consumer retry topics with bounded exponential backoff.
- [ ] Expose producer and consumer metrics in Prometheus format.
- [ ] Add a consumer-lag dashboard and a reproducible lag scenario.
- [ ] Benchmark symbol-based versus account-based partitioning.
- [ ] Add a transactional consume-transform-produce example.
- [ ] Add graceful shutdown and rebalance callback tests.
- [ ] Introduce Testcontainers-based Kafka integration tests.

## Later

- [ ] Add Debezium CDC from PostgreSQL.
- [ ] Add stream aggregation for one-minute notional volume.
- [ ] Add a compacted topic containing the latest instrument state.
- [ ] Demonstrate outbox pattern delivery guarantees.
- [ ] Add OpenTelemetry traces across producer and consumer.
- [ ] Run a controlled broker outage and document recovery behavior.
- [ ] Compare Avro schema evolution with Protobuf for one event.

## Completed baseline

- [x] Local Kafka-compatible broker and Schema Registry.
- [x] Avro `TradeExecuted` event.
- [x] Typed Python producer and consumer.
- [x] Unit tests, linting, formatting, typing, and CI.
- [x] Guarded scheduled agent workflow that opens pull requests.
