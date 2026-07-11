# Design Tradeoffs

## Local Mock Providers vs Real APIs

InferenceOps Gateway uses local mock providers instead of paid external APIs.

This keeps the project free, reproducible, and safe to run without API keys. The tradeoff is that the project does not measure real model quality or real provider latency.

The goal is to study gateway-level behavior such as caching, rate limiting, budget enforcement, logging, and routing.

## Exact Cache vs Semantic Cache

v0.2 uses an exact cache.

A cache hit requires the normalized prompt, selected model, temperature, max tokens, prompt template version, and model version to match.

This gives stronger correctness guarantees. The tradeoff is a lower cache hit rate compared with semantic cache.

Semantic cache may improve the hit rate, but it can introduce false-positive cache hits where two similar prompts require different answers. Semantic cache is future work.

## Fixed Window vs Token Bucket

v0.2 uses fixed-window rate limiting with Redis.

The key format is:

```text
rate_limit:{user_id}:{yyyyMMddHHmm}
```

This is simple, fast, and easy to explain.

The tradeoff is boundary bursts. A user may send requests at the end of one minute and again at the start of the next minute, briefly exceeding the intended smooth rate.

Token bucket or sliding-window counters would be better future implementations.

## Daily Budget Enforcement

v0.2 rejects requests when the projected daily estimated spend exceeds the user's configured daily budget.

The current design checks:

```text
today_estimated_spend + current_request_estimated_cost <= daily_budget
```

If the projected spend exceeds the budget, the gateway returns an error before calling the provider.

This protects the system from accidental overuse. The tradeoff is that the current implementation uses simulated estimated cost instead of real provider billing.

## PostgreSQL Logging vs Redis-Only Counters

Request metadata is stored in PostgreSQL because request logs are durable and queryable.

Redis is used for temporary cache and rate-limit counters.

The tradeoff is that PostgreSQL writes are slower than Redis writes, but the project needs durable historical logs for debugging, usage tracking, and benchmark analysis.

## Docker Compose vs Kubernetes

v0.2 uses Docker Compose.

Docker Compose is enough for a local-first portfolio project and keeps the development environment simple.

Kubernetes would add operational complexity that is not needed for v1.0.

## Why No Frontend

This project focuses on backend and AI infrastructure.

A frontend would not help demonstrate the core technical ideas: caching, rate limiting, budget enforcement, request logging, and provider abstraction.

## Why No Paid APIs

The project intentionally avoids paid APIs to keep it reproducible, free, and safe to run by anyone cloning the repository.

### Cache Hit Cost Semantics

`estimated_cost_usd` represents the simulated provider cost incurred by the current gateway request.

A cache miss that calls a mock provider records the estimated provider cost. A cache hit records zero provider cost because no provider call occurs.

This allows daily budget calculations and future benchmarks to measure provider cost reduction from caching correctly.

## Redis Persistence Strategy

PostgreSQL is the system of record and uses a Docker named volume so that users, model prices, request logs, and migration state survive container recreation.

Redis is intentionally treated as ephemeral infrastructure in v0.2 and does not use a persistent volume.

The following Redis data may be lost when the Redis container is removed or recreated:

- Exact-cache entries
- Rate-limit counters
- Temporary test keys

This is acceptable because cache entries can be regenerated and rate-limit counters are short-lived control data.

The consequence is that after a Redis restart:

- The next repeated inference request becomes a cache miss.
- Rate-limit counters restart from zero.
- PostgreSQL request history remains unchanged.

This is a deliberate local-first design decision, not accidental data loss.