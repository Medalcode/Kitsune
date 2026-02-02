# Architecture Decision Record

## Overview

Kitsune implements a **layered architecture** with clear separation of concerns. This document explains the rationale behind key architectural decisions.

---

## Core Principles

### 1. **Async-First**

**Decision**: Use SQLAlchemy async + asyncpg for all database operations.

**Rationale**:

- Non-blocking I/O allows handling more concurrent requests with fewer resources
- FastAPI is built on ASGI (async), blocking calls waste the event loop
- PostgreSQL's asyncpg driver is significantly faster than psycopg2

**Trade-offs**:

- Slightly more complex code (async/await everywhere)
- Can't use some legacy SQLAlchemy patterns (e.g., lazy loading)

**When to reconsider**: If you need to integrate with sync-only libraries or have a team unfamiliar with async Python.

---

### 2. **Repository Pattern**

**Decision**: Separate data access (repositories) from business logic (services).

**Rationale**:

- **Testability**: Mock repositories in unit tests without touching the DB
- **Maintainability**: Change DB queries without touching business logic
- **Reusability**: Same repository methods used across multiple services

**Implementation**:

```python
# Repository: "How to get data"
class UserRepository:
    async def get_by_email(self, email: str) -> User | None:
        query = select(User).filter(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

# Service: "What to do with data"
class UserService:
    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError()
        return user
```

**Trade-offs**:

- More files and boilerplate
- Overkill for simple CRUD operations

**When to reconsider**: For very simple APIs with <5 models and no complex queries.

---

### 3. **No Unit of Work (Yet)**

**Decision**: Repositories commit directly. No UoW pattern implemented.

**Current State**:

```python
# BaseRepository.create() does commit
async def create(self, obj_in: dict) -> ModelType:
    db_obj = self.model(**obj_in)
    self.db.add(db_obj)
    await self.db.commit()  # ⚠️ Commits immediately
    return db_obj
```

**Known Issue**: Can't do atomic multi-entity transactions.

**Roadmap**: Implement Unit of Work pattern when we need:

- Multi-step transactions (e.g., create user + send email + log audit)
- Explicit rollback control
- Better testing (mock commits)

**Why not now**: YAGNI (You Aren't Gonna Need It). Current use cases don't require complex transactions.

---

### 4. **Pydantic for Validation, SQLAlchemy for Persistence**

**Decision**: Separate schemas (Pydantic) from models (SQLAlchemy).

**Rationale**:

- **API contracts ≠ DB schema**: API might expose a subset of fields
- **Validation**: Pydantic validates incoming data before it touches the DB
- **Serialization**: Pydantic handles JSON encoding (dates, decimals, etc.)

**Example**:

```python
# Schema (API layer)
class UserCreate(BaseModel):
    email: EmailStr
    password: str  # Plain password from client

# Model (DB layer)
class User(Base):
    email = Column(String)
    hashed_password = Column(String)  # Never exposed in API
```

**Trade-offs**:

- Duplication between schemas and models
- Need to manually map between them

**Alternative considered**: SQLModel (combines Pydantic + SQLAlchemy). Rejected because:

- Less mature than SQLAlchemy
- Harder to customize complex queries
- Tight coupling between API and DB

---

### 5. **Dependency Injection via FastAPI**

**Decision**: Use FastAPI's `Depends()` for all cross-cutting concerns.

**Rationale**:

- **Testability**: Override dependencies in tests (e.g., mock DB session)
- **Clarity**: Explicit dependencies in function signatures
- **No magic**: No global state or singletons

**Example**:

```python
# Dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Usage
@router.get("/users/")
async def list_users(db: AsyncSession = Depends(get_db)):
    # db is injected, no global imports
    ...
```

**Why not a DI container** (e.g., `dependency-injector`):

- FastAPI's DI is sufficient for most cases
- External DI adds complexity and learning curve
- Harder to debug (implicit wiring)

---

### 6. **Structured Logging**

**Decision**: Use `structlog` for JSON-formatted logs.

**Rationale**:

- **Machine-readable**: Easy to parse in log aggregators (Datadog, CloudWatch)
- **Contextual**: Attach request IDs, user IDs, etc. to all logs
- **Queryable**: Filter logs by structured fields, not regex

**Example**:

```python
logger.info(
    "user_created",
    user_id=user.id,
    email=user.email,
    duration_ms=elapsed
)
# Output: {"event": "user_created", "user_id": 123, "email": "...", ...}
```

**Trade-offs**:

- Less human-readable in development (use `ConsoleRenderer` for local)
- Requires log aggregation tool to be useful

---

### 7. **Alembic for Migrations**

**Decision**: Use Alembic for schema versioning, not `create_all()`.

**Rationale**:

- **Version control**: Track schema changes in Git
- **Rollback**: Downgrade migrations if deployment fails
- **Team coordination**: Avoid "works on my machine" DB issues

**Workflow**:

```bash
# After changing a model
alembic revision --autogenerate -m "Add products table"
alembic upgrade head
```

**Why not Django-style migrations**: Alembic is the standard for SQLAlchemy.

---

### 8. **No ORM Relationships (Yet)**

**Decision**: Models don't define relationships (`relationship()`, `backref`).

**Current State**:

```python
# No relationships defined
class User(Base):
    id = Column(Integer, primary_key=True)
    # No: posts = relationship("Post", back_populates="author")
```

**Rationale**:

- **Simplicity**: Fewer implicit queries (N+1 problem)
- **Explicit joins**: Write joins manually in repositories
- **Async-friendly**: Lazy loading doesn't work well with async

**When to add**: When you have >3 related entities and need eager loading.

---

### 9. **PostgreSQL as Default**

**Decision**: PostgreSQL for production, SQLite for tests.

**Rationale**:

- **PostgreSQL**: Industry standard, robust, great async support
- **SQLite in tests**: Fast, no external dependencies, isolated

**Why not MySQL**: PostgreSQL has better JSON support, full-text search, and async drivers.

**Why not MongoDB**: This is a relational data template. Use a different stack for document DBs.

---

### 10. **Docker Multi-Stage Builds**

**Decision**: Use multi-stage Dockerfile to minimize image size.

**Rationale**:

- **Security**: Final image doesn't include build tools (gcc, etc.)
- **Size**: ~200MB final image vs ~800MB with build deps
- **Speed**: Faster deployments and container startup

**Implementation**:

```dockerfile
# Stage 1: Build wheels
FROM python:3.11-slim as builder
RUN pip install poetry
RUN poetry export -o requirements.txt
RUN pip wheel --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
```

---

## What We Explicitly Avoid

### ❌ **CQRS (Command Query Responsibility Segregation)**

**Why**: Overkill for most APIs. Adds complexity without clear benefit until you have:

- Separate read/write databases
- Event sourcing
- High read/write ratio (>100:1)

### ❌ **Microservices**

**Why**: This is a template for a **single service**. Microservices introduce:

- Network latency
- Distributed transactions
- Service discovery
- Operational complexity

Start with a monolith. Split when you have a clear reason (team scaling, different SLAs).

### ❌ **GraphQL**

**Why**: REST is simpler and well-understood. GraphQL adds:

- Query complexity attacks
- N+1 query problems
- Schema stitching complexity

Use GraphQL if your frontend needs flexible queries. Otherwise, REST is sufficient.

### ❌ **Celery/Background Tasks**

**Why**: Not included by default because:

- Most APIs don't need async tasks initially
- Adds Redis/RabbitMQ dependency
- Operational overhead (worker monitoring)

Add when you need: email sending, report generation, long-running jobs.

---

## Future Considerations

### When to Refactor

**Add Unit of Work** when:

- You have multi-step transactions that must be atomic
- You need explicit rollback control
- Testing becomes painful due to commits in repositories

**Add RBAC** when:

- You have >2 user types (e.g., admin, editor, viewer)
- Permissions are dynamic (not hardcoded)
- You need audit logs of permission changes

**Split into Microservices** when:

- Team size >10 developers
- Different parts of the system have different scaling needs
- You need to deploy components independently

**Add Event Sourcing** when:

- You need full audit trail of all changes
- You need to replay events
- You need temporal queries ("what was the state 3 months ago?")

---

## References

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [SQLAlchemy Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Twelve-Factor App](https://12factor.net/)

---

**Last Updated**: 2026-02-01  
**Version**: 0.1.0
