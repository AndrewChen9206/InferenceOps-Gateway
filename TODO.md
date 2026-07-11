# TODO

## Current Milestone: Finish v0.1

### Documentation

- [ ] Write README.md v0.1
- [ ] Write ARCHITECTURE.md v0.1
- [ ] Write ROADMAP.md
- [ ] Write TODO.md
- [ ] Add .gitignore

### Testing

- [ ] Add health endpoint tests
- [ ] Add inference endpoint test
- [ ] Add unknown user test
- [ ] Run `uv run pytest`
- [ ] Run `uv run ruff format`
- [ ] Run `uv run ruff check`

### GitHub

- [ ] Initialize git repository if needed
- [ ] Commit v0.1 code
- [ ] Create empty GitHub repository
- [ ] Push local repository to GitHub

## Next Milestone: v0.2 Cache + Control Layer

### Cache

- [x] Design exact cache key format
- [x] Add cache key version
- [x] Add Redis cache lookup
- [x] Add Redis cache write
- [x] Add TTL
- [x] Log cache hit/miss
- [x] Add cache API tests

### Cost Control

- [ ] Add daily usage query
- [ ] Add budget enforcement
- [ ] Add budget rejection error response
- [ ] Add budget tests

### Rate Limiting

- [x] Add Redis fixed-window counter
- [x] Add rate limit error response
- [x] Add rate limit tests
- [x] Document fixed-window tradeoffs

## v0.2 Cache + Control Layer

Status: Complete

- [x] Containerize FastAPI
- [x] Add Alembic schema migrations
- [x] Add Docker Compose migration service
- [x] Add exact Redis cache
- [x] Add versioned cache keys
- [x] Add TTL
- [x] Add cache hit/miss logging
- [x] Record zero provider cost for cache hits
- [x] Add fixed-window rate limiting
- [x] Add daily budget enforcement
- [x] Add structured domain errors
- [x] Add best-effort cache write strategy
- [x] Separate development and test infrastructure
- [x] Add automated tests and design documentation