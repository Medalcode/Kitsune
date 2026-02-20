# Kitsune

**Production-ready FastAPI template with async SQLAlchemy, JWT authentication, and clean architecture.**

Built for teams that need to ship secure, scalable APIs without reinventing the wheel.

---

## Why Kitsune?

Most FastAPI templates are either too basic (hello world with SQLite) or over-engineered (microservices with Kafka for a CRUD app). Kitsune sits in the sweet spot:

- **Battle-tested patterns**: Repository pattern, dependency injection, structured logging
- **Async-first**: SQLAlchemy async, PostgreSQL, Redis-ready
- **Security by default**: JWT with proper validation, bcrypt hashing, CORS configuration
- **Production-ready**: Docker multi-stage builds, Alembic migrations, health checks
- **Developer experience**: Poetry, Ruff linting, pytest with async fixtures

**What Kitsune is NOT**: A framework, a boilerplate generator, or a one-size-fits-all solution. It's a starting point with opinionated defaults that you can adapt.

---

## Quick Start

### Prerequisites

- Python 3.10+
- Docker (optional, for PostgreSQL + Redis)

### Local Development

```bash
# Install dependencies
poetry install

# Run with auto-reload
poetry run uvicorn src.app.main:app --reload
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### Docker (Recommended)

```bash
docker-compose up --build
```

Includes PostgreSQL, Redis, and the API with hot-reload.

---

## Core Features

### 🔐 Authentication & Authorization

- JWT-based authentication (OAuth2 password flow)
- Bcrypt password hashing (configurable rounds)
- User activation/deactivation
- Dependency-based route protection

```python
@router.get("/protected")
async def protected_route(
    current_user: User = Depends(deps.get_current_active_user)
):
    return {"user_id": current_user.id}
```

### 🗄️ Database Layer

- **Async SQLAlchemy 2.0**: Non-blocking I/O for better concurrency
- **Repository Pattern**: Decouples business logic from data access
- **Alembic Migrations**: Version-controlled schema changes
- **PostgreSQL-first**: SQLite for tests, Postgres for production

```python
# Clean separation of concerns
class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create(self, user_in: UserCreate) -> User:
        # Business logic here
        return await self.repository.create(user_data)
```

### 📊 Observability

- **Structured logging** with `structlog` (JSON output for production)
- **Request/response middleware** with timing and correlation IDs
- **Health check endpoint** (ready for Kubernetes probes)

### 🧪 Testing

- Pytest with async support
- In-memory SQLite for fast tests
- Pre-configured fixtures (DB session, HTTP client, auth tokens)
- Example integration tests included

---

## Architecture

```
src/app/
├── api/
│   ├── deps.py              # Shared dependencies (auth, DB session)
│   └── v1/
│       ├── endpoints/       # Route handlers
│       └── router.py        # API router aggregation
├── core/
│   ├── config.py            # Settings (env-based)
│   ├── security.py          # JWT + password hashing
│   ├── logging.py           # Structured logging setup
│   └── exceptions.py        # Global exception handlers
├── db/
│   └── session.py           # Async engine + session factory
├── models/                  # SQLAlchemy ORM models
├── repositories/            # Data access layer
│   ├── base.py              # Generic CRUD operations
│   └── user_repository.py   # User-specific queries
├── schemas/                 # Pydantic models (validation)
├── services/                # Business logic layer
└── main.py                  # FastAPI app factory
```

**Design Principles**:

- **Layered architecture**: API → Service → Repository → DB
- **Dependency injection**: FastAPI's `Depends()` for testability
- **Separation of concerns**: Models (DB) ≠ Schemas (API)
- **Async all the way**: No blocking I/O in the request path

---

## Configuration

Environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/kitsune

# Security (CRITICAL: Change in production)
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (optional, for caching/rate limiting)
REDIS_URL=redis://localhost:6379/0
```

**Production checklist**:

- [ ] Generate a secure `SECRET_KEY` (32+ characters)
- [ ] Set `DATABASE_ECHO=false` to disable SQL logging
- [ ] Configure `BACKEND_CORS_ORIGINS` with your frontend domain
- [ ] Use a managed PostgreSQL instance (not SQLite)
- [ ] Enable HTTPS (Kitsune assumes you're behind a reverse proxy)

---

## Extending Kitsune

### Agents & Skills

Kitsune soporta patrones de orquestación y capacidades reutilizables documentadas en:

- [Agents (concepto y pautas)](docs/agents.md)
- [Skills (diseño y mejores prácticas)](docs/skills.md)

Estos documentos explican cuándo extraer lógica a `skills` reutilizables y cómo los `agents` deben orquestar esas capacidades en background o flujos asincrónicos.


### Adding a New Resource

1. **Model** (`src/app/models/product.py`):

```python
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2))
```

2. **Schema** (`src/app/schemas/product.py`):

```python
class ProductCreate(BaseModel):
    name: str
    price: Decimal

class Product(ProductCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

3. **Repository** (`src/app/repositories/product_repository.py`):

```python
class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_name(self, name: str) -> Product | None:
        query = select(Product).filter(Product.name == name)
        result = await self.db.execute(query)
        return result.scalars().first()
```

4. **Service** (`src/app/services/product_service.py`):

```python
class ProductService:
    def __init__(self, db: AsyncSession):
        self.repository = ProductRepository(db)

    async def create(self, product_in: ProductCreate) -> Product:
        return await self.repository.create(product_in.model_dump())
```

5. **Endpoint** (`src/app/api/v1/endpoints/products.py`):

```python
@router.post("/", response_model=schemas.Product)
async def create_product(
    product_in: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return await service.create(product_in)
```

6. **Migration**:

```bash
alembic revision --autogenerate -m "Add products table"
alembic upgrade head
```

---

## Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=src --cov-report=html

# Specific test file
poetry run pytest tests/integration/api/test_auth.py -v
```

**Test structure**:

- `tests/unit/`: Pure logic (no DB, no HTTP)
- `tests/integration/`: API endpoints + DB interactions
- `tests/e2e/`: Full user journeys

See `docs/TESTING.md` for detailed testing strategy.

---

## Deployment

### Docker Production Build

```dockerfile
# Already optimized:
# - Multi-stage build (smaller image)
# - Non-root user (security)
# - Poetry export to requirements.txt (faster installs)
```

```bash
docker build -t kitsune:latest .
docker run -p 8000:8000 --env-file .env kitsune:latest
```

### Kubernetes

Example deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kitsune-api
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: api
          image: kitsune:latest
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: kitsune-secrets
                  key: database-url
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
          readinessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
```

---

## Roadmap

Current version: **v0.1.0** (MVP)

### Implemented ✅

- [x] JWT authentication
- [x] Repository pattern
- [x] Async SQLAlchemy
- [x] Structured logging
- [x] Docker setup
- [x] Alembic migrations
- [x] Basic tests

### Planned 🚧

- [ ] Refresh tokens (revocable sessions)
- [ ] Rate limiting (Redis-based)
- [ ] Role-based access control (RBAC)
- [ ] Password reset flow (email + token)
- [ ] Prometheus metrics
- [ ] OpenTelemetry tracing

See `BITACORA.md` for detailed changelog and technical decisions.

---

## Contributing

This is a template, not a library. Fork it, adapt it, make it yours.

If you find a security issue or a critical bug, open an issue. For feature requests, consider if they belong in a template or in your specific implementation.

---

## License

MIT License - Use it however you want, no strings attached.

---

## Acknowledgments

Built with:

- [FastAPI](https://fastapi.tiangolo.com/) by Sebastián Ramírez
- [SQLAlchemy](https://www.sqlalchemy.org/) by Mike Bayer
- [Pydantic](https://docs.pydantic.dev/) by Samuel Colvin
- [Structlog](https://www.structlog.org/) by Hynek Schlawack

Inspired by production APIs at scale, not by tutorials.

---

**Questions?** Check `docs/GUIDE.md` for detailed usage examples.

**Need help?** This is a template, not a support project. Read the code, it's well-documented.
