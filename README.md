# InferenceOps Gateway

A local-first, cache-aware and cost-aware AI inference gateway for document-AI workloads.

## Overview

InferenceOps Gateway is a production-inspired backend / AI infrastructure project. It simulates an internal inference gateway that applications call before reaching an AI model provider.

The project is fully local and uses mock providers instead of paid APIs. The goal is not to build a chatbot or a real LLM product. The goal is to demonstrate backend mechanisms behind production AI systems: API design, request validation, provider abstraction, PostgreSQL logging, Redis readiness, simulated cost estimation, and clean service layering.

## Motivation

My previous work was mostly applied AI, such as OCR evaluation and RF classification. I realized that model accuracy is only one part of production AI. Once AI workloads have real users, backend teams also need to control latency, cost, caching, rate limits, fallback, retries, observability, and request logging.

InferenceOps Gateway is my local-first way to study that infrastructure layer.

## Current Status: v0.1 Gateway Skeleton

v0.1 implements the first vertical slice:

- FastAPI application
- Docker Compose for PostgreSQL and Redis
- `/healthz` endpoint
- `/readyz` endpoint
- SQLAlchemy async database setup
- PostgreSQL models for users, model prices, and request logs
- Seed data for default user and mock model prices
- Mock provider
- `/v1/infer` endpoint
- Request logging to PostgreSQL
- Basic pytest coverage for health and inference API behavior

## Tech Stack

- Python 3.12
- FastAPI
- Pydantic v2
- Uvicorn
- uv
- PostgreSQL
- SQLAlchemy 2.x async
- asyncpg
- Redis
- Docker Compose
- pytest
- ruff

## Architecture Preview

```text
Client
  |
  v
FastAPI Router
  |
  v
Inference Service
  |-------------------|
  v                   v
Repository        Mock Provider
  |
  v
PostgreSQL

Redis is available and checked by /readyz, but caching and rate limiting are planned for v0.2.
```

## Local Quickstart

### 1. Install dependencies

```bash
uv sync
```

### 2. Start local infrastructure

```bash
docker compose up -d
docker compose ps
```

PostgreSQL and Redis should be healthy before starting the API.

### 3. Configure environment

```bash
cp .env.example .env
```

For local development where FastAPI runs in WSL and PostgreSQL/Redis run in Docker, use:

```env
POSTGRES_HOST=localhost
REDIS_HOST=localhost
```

### 4. Start the API

```bash
uv run uvicorn app.main:app --reload
```

### 5. Test health endpoints

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

### 6. Send an inference request

```bash
curl -X POST http://localhost:8000/v1/infer \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "andrew",
    "task_type": "ocr_cleanup",
    "prompt": "Clean and normalize this OCR text...",
    "policy": "cost_aware",
    "temperature": 0.0,
    "max_tokens": 256,
    "cache": true
  }'
```

## API Endpoints

### GET /healthz

Checks whether the FastAPI app is alive.

### GET /readyz

Checks whether PostgreSQL and Redis are reachable.

### POST /v1/infer

Runs a simulated inference request through the gateway.

Current v0.1 behavior:

1. Validate request body.
2. Check that the user exists.
3. Normalize and hash the prompt.
4. Select the v0.1 mock provider.
5. Estimate input/output tokens.
6. Estimate simulated cost.
7. Generate a mock response.
8. Write request metadata to PostgreSQL.
9. Return a structured response.

## Testing

Run:

```bash
uv run pytest
```

Run linting / formatting:

```bash
uv run ruff format
uv run ruff check
```

## v0.2 Cache Flow

```text
Client
  |
  v
POST /v1/infer
  |
  v
Inference Service
  |
  v
Build exact cache key
  |
  +--> Cache hit?
       |
       +--> Yes
       |     |
       |     v
       |  Redis cached response
       |     |
       |     v
       |  PostgreSQL log
       |     |
       |     v
       |  Response
       |
       +--> No
             |
             v
        Mock Provider
             |
             v
        Redis write
             |
             v
        PostgreSQL log
             |
             v
          Response
```

The cache key includes:

- Task type
- Selected model
- Normalized prompt
- Temperature
- Max tokens
- Cache key version
- Prompt template version
- Model version

The raw prompt is **never** used directly as the Redis key.

Instead, the cache key is serialized and hashed using **SHA-256** before being stored in Redis.

## Limitations

v0.1 is intentionally small. It does not yet implement:

- Redis exact caching
- Rate limiting
- Daily budget enforcement
- Multiple routing policies
- Provider fallback
- Prometheus metrics
- Benchmark runner
- Alembic migrations

These are planned for future phases.

## Roadmap

- v0.1: Gateway skeleton
- v0.2: Cache + control layer
- v0.3: Routing + fallback + metrics
- v1.0: Benchmarks + portfolio documentation

## Interview Positioning

This is a production-inspired educational portfolio project. It does not replace Cloudflare AI Gateway, LiteLLM, Portkey, or other production systems. The goal is to understand and demonstrate the backend mechanisms behind such systems in a fully local and reproducible way.

