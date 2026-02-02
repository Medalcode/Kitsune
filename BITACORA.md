# Bitácora Técnica - Kitsune

**Changelog de decisiones arquitectónicas y evolución del proyecto.**

---

## v0.1.0 - MVP Foundation (2026-02-01)

### Architectural Decisions

#### 1. Repository Pattern Implementation

**Rationale**: Separate data access from business logic for better testability and maintainability.

**Changes**:

- Created `BaseRepository[T]` with generic CRUD operations
- Implemented `UserRepository` with domain-specific queries (`get_by_email`)
- Refactored `UserService` to depend on repositories instead of raw DB sessions

**Trade-offs**:

- ✅ Easier to mock in tests
- ✅ Centralized query logic
- ❌ More boilerplate (extra layer)

**Known Issue**: Repositories commit directly (no Unit of Work pattern). This limits atomic multi-entity transactions. Acceptable for MVP, will revisit when needed.

---

#### 2. Async SQLAlchemy 2.0

**Rationale**: Non-blocking I/O for better concurrency under load.

**Changes**:

- Migrated from sync to async engine (`create_async_engine`)
- Used `AsyncSession` throughout the stack
- Configured `asyncpg` driver for PostgreSQL

**Performance Impact**:

- ~3x more concurrent requests per worker (measured with `wrk`)
- No blocking I/O in request path

**Gotchas**:

- Can't use lazy loading (relationships must be eagerly loaded)
- All DB calls must be `await`ed

---

#### 3. PostgreSQL as Default

**Rationale**: Production-grade database with excellent async support.

**Changes**:

- Default `DATABASE_URL` points to PostgreSQL
- SQLite used only in tests (in-memory, fast isolation)
- Added `asyncpg` dependency

**Why not MySQL**: PostgreSQL has better JSON support, full-text search, and mature async drivers.

---

#### 4. Structured Logging with Structlog

**Rationale**: Machine-readable logs for production observability.

**Changes**:

- Replaced print statements with `structlog`
- JSON output in production, console renderer in development
- Added request timing middleware

**Example Output**:

```json
{
  "event": "request_processed",
  "method": "POST",
  "path": "/api/v1/users/",
  "status": 200,
  "duration_ms": 45.2,
  "timestamp": "2026-02-01T23:00:00Z"
}
```

---

#### 5. Docker Multi-Stage Build

**Rationale**: Smaller images, faster deployments, better security.

**Changes**:

- Stage 1: Build wheels with Poetry
- Stage 2: Runtime-only image (no build tools)
- Non-root user (`appuser`)

**Results**:

- Image size: ~220MB (vs ~850MB single-stage)
- Build time: ~2min (cached layers)

---

### Security Improvements

#### JWT Authentication

**Implementation**:

- HS256 algorithm (symmetric key)
- 30-minute token expiration
- Bcrypt password hashing (12 rounds)

**Known Gaps** (documented in `docs/SECURITY.md`):

- No refresh tokens (users re-login every 30min)
- No token revocation mechanism
- CORS open by default (`allow_origins=["*"]`)

**Roadmap**: Refresh tokens in v0.2.0, RBAC in v0.3.0.

---

### DevOps & Tooling

#### Poetry Migration

**Why**: Deterministic builds, better dependency resolution than pip.

**Changes**:

- Migrated from `requirements.txt` to `pyproject.toml`
- Locked dependencies in `poetry.lock`
- Updated CI/CD to use Poetry

---

#### GitHub Actions CI

**Pipeline**:

1. Lint with Ruff (format check + error detection)
2. Run tests with pytest
3. (Future) Build Docker image and push to registry

**Missing**: Integration tests with real PostgreSQL (currently uses SQLite).

---

## Roadmap

### v0.2.0 - Security Hardening (Planned)

- [ ] Implement refresh tokens
- [ ] Add rate limiting (Redis-based)
- [ ] Fix CORS configuration (whitelist origins)
- [ ] Add security headers (HSTS, CSP, etc.)
- [ ] Timing attack mitigation in login

### v0.3.0 - RBAC & Audit (Planned)

- [ ] Role-based access control
- [ ] Audit log table (who did what, when)
- [ ] Admin endpoints (user management)

### v1.0.0 - Production Ready (Planned)

- [ ] Password reset flow (email + token)
- [ ] MFA support (TOTP)
- [ ] Prometheus metrics
- [ ] OpenTelemetry tracing
- [ ] Health check endpoint

---

## Technical Debt

### High Priority

1. **Unit of Work Pattern**: Repositories commit directly, can't do atomic multi-entity transactions.
   - **Impact**: Can't rollback partial operations
   - **Fix**: Implement UoW when we add complex business logic

2. **No Token Revocation**: JWTs can't be invalidated before expiration.
   - **Impact**: Stolen tokens are valid until expiry
   - **Fix**: Add refresh tokens + token blacklist (Redis)

### Medium Priority

3. **SQL Logs in Production**: `echo=True` hardcoded in `session.py`.
   - **Impact**: Performance degradation, potential data leak
   - **Fix**: Make `echo` configurable via env var

4. **No Integration Tests with Postgres**: Tests use SQLite, not production DB.
   - **Impact**: Might miss Postgres-specific bugs
   - **Fix**: Add GitHub Actions service container

### Low Priority

5. **No Observability Metrics**: Only logs, no Prometheus metrics.
   - **Impact**: Can't track request rate, error rate, latency percentiles
   - **Fix**: Add `prometheus-fastapi-instrumentator`

---

## Lessons Learned

### What Worked Well

- **Repository Pattern**: Made testing much easier (mock repositories, not DB)
- **Async SQLAlchemy**: Noticeable performance improvement under load
- **Structlog**: JSON logs are a game-changer for debugging in production

### What Didn't Work

- **Initial CORS Config**: `allow_origins=["*"]` is insecure, should have been explicit from day 1
- **Committing in Repositories**: Should have implemented UoW from the start

### Surprises

- **Bcrypt Performance**: 12 rounds is ~100ms per hash. Acceptable for login, but consider caching for high-traffic endpoints.
- **Alembic Autogenerate**: Works 90% of the time, but always review generated migrations.

---

## References

- [Architecture Decisions](docs/ARCHITECTURE.md)
- [Security Considerations](docs/SECURITY.md)
- [Testing Strategy](docs/TESTING.md) (planned)

---

**Last Updated**: 2026-02-01  
**Current Version**: v0.1.0 (MVP)
