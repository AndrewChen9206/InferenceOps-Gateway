# Rate Limiting Notes

## Why Rate Limiting Matters

Rate limiting protects the gateway from abusive or accidental overuse. Even when requests are served from cache, they still consume gateway resources such as HTTP handling, Redis access, PostgreSQL logging, and application CPU time.

## Current Implementation

v0.2 uses fixed-window rate limiting backed by Redis.

Each request increments a Redis counter:

```text
rate_limit:{user_id}:{yyyyMMddHHmm}

Example:

rate_limit:andrew:202607081430
```

This key represents Andrew's request count during the 14:30 minute window.

### Redis Operations

The implementation uses:

- `INCR`
- `EXPIRE`

Flow:

1. Build the current minute key.
2. Increment the key.
3. If this is the first request in the window, set a 60-second expiration.
4. Allow the request if `count <= user limit`.
5. Reject the request if `count > user limit`.

## Why Fixed Window?

Fixed-window rate limiting is simple, fast, and easy to explain. It is a good MVP choice for this portfolio project.

### Tradeoff: Boundary Burst

Fixed windows can allow bursts near time boundaries.

Example:

```text
12:00:59 -> user sends 60 requests
12:01:00 -> user sends another 60 requests
```

Even with a 60 requests/minute limit, the user may send 120 requests in a very short period.

## Alternatives

### Token Bucket

A token bucket allows requests while tokens are available and refills tokens over time. It handles bursts more smoothly.

### Sliding Window Counter

A sliding-window counter estimates request volume over a rolling window instead of a fixed calendar minute.

## Current Design Decision

v0.2 uses fixed-window rate limiting because the goal is to demonstrate gateway control behavior clearly without over-engineering.

Future versions may replace it with token bucket or sliding-window rate limiting.
