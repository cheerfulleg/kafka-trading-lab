# ADR 0001: Use Redpanda for the local Kafka-compatible stack

- Status: Accepted
- Date: 2026-07-24

## Context

The lab needs Kafka protocol behavior, Schema Registry, and a browser console
without a large local cluster or several separately configured containers.

## Decision

Use a single-node Redpanda broker for local development. Applications use only
Kafka and Schema Registry APIs through `confluent-kafka`; business code must not
depend on Redpanda-specific client APIs.

## Consequences

- The lab starts quickly and has a compact Docker Compose file.
- Schema Registry and the console are available immediately.
- Broker-specific experiments must be verified against Apache Kafka before
  making general claims about Kafka behavior.
- A future integration-test profile may use Testcontainers with Apache Kafka.
