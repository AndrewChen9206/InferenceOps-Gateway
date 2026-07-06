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

- [ ] Design exact cache key format
- [ ] Add cache key version
- [ ] Add prompt normalization tests
- [ ] Add Redis cache lookup
- [ ] Add Redis cache write
- [ ] Add TTL
- [ ] Log cache hit/miss

### Cost Control

- [ ] Add daily usage query
- [ ] Add budget enforcement
- [ ] Add budget rejection error response
- [ ] Add budget tests

### Rate Limiting

- [ ] Add Redis fixed-window counter
- [ ] Add rate limit error response
- [ ] Add rate limit tests
- [ ] Document fixed-window tradeoffs
