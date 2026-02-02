# Quick Reference

**Fast lookup for common tasks in Kitsune.**

---

## Environment Setup

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run development server
poetry run uvicorn src.app.main:app --reload

# Run with Docker
docker-compose up --build
```

---

## Database Operations

### Migrations

```bash
# Create migration (after changing models)
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Direct DB Access

```bash
# Connect to PostgreSQL (Docker)
docker-compose exec db psql -U postgres -d kitsune

# Useful queries
SELECT * FROM users;
SELECT * FROM alembic_version;
```

---

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/integration/api/test_auth.py

# Run specific test
poetry run pytest tests/integration/api/test_auth.py::TestLogin::test_login_with_valid_credentials -v

# Run only unit tests (fast)
poetry run pytest tests/unit -v

# Run in parallel (faster)
poetry run pytest -n auto
```

---

## Code Quality

```bash
# Format code
poetry run ruff format .

# Check linting
poetry run ruff check .

# Auto-fix linting issues
poetry run ruff check --fix .

# Check formatting without changing files
poetry run ruff format --check .
```

---

## API Usage

### Create User

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### Login (Get Token)

```bash
curl -X POST http://localhost:8000/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123"

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

### Access Protected Endpoint

```bash
TOKEN="your_access_token_here"

curl -X GET http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Common Patterns

### Add New Endpoint

1. **Create schema** (`src/app/schemas/product.py`):

```python
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float

class Product(ProductCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

2. **Create model** (`src/app/models/product.py`):

```python
from sqlalchemy import Column, Integer, String, Numeric
from src.app.db.session import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2))
```

3. **Create repository** (`src/app/repositories/product_repository.py`):

```python
from src.app.repositories.base import BaseRepository
from src.app.models.product import Product

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db):
        super().__init__(Product, db)
```

4. **Create service** (`src/app/services/product_service.py`):

```python
from src.app.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, db):
        self.repository = ProductRepository(db)

    async def create(self, product_in):
        return await self.repository.create(product_in.model_dump())
```

5. **Create endpoint** (`src/app/api/v1/endpoints/products.py`):

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.session import get_db
from src.app.services.product_service import ProductService
from src.app import schemas

router = APIRouter()

@router.post("/", response_model=schemas.Product)
async def create_product(
    product_in: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    return await service.create(product_in)
```

6. **Register router** (`src/app/api/v1/router.py`):

```python
from src.app.api.v1.endpoints import products

api_router.include_router(products.router, prefix="/products", tags=["products"])
```

7. **Create migration**:

```bash
alembic revision --autogenerate -m "Add products table"
alembic upgrade head
```

---

### Protect Endpoint with Auth

```python
from src.app.api import deps
from src.app import models

@router.get("/protected")
async def protected_route(
    current_user: models.User = Depends(deps.get_current_active_user)
):
    return {"user_id": current_user.id, "email": current_user.email}
```

---

### Add Custom Query to Repository

```python
# In UserRepository
async def get_active_users(self) -> list[User]:
    query = select(User).filter(User.is_active == True)
    result = await self.db.execute(query)
    return result.scalars().all()
```

---

## Configuration

### Environment Variables

```bash
# .env file
PROJECT_NAME="My API"
API_V1_STR="/api/v1"

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname

# Security (CHANGE IN PRODUCTION)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS (comma-separated)
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Generate Secure Secret Key

```bash
openssl rand -hex 32
```

---

## Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Rebuild only API service
docker-compose up --build api

# Execute command in container
docker-compose exec api poetry run alembic upgrade head
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Ensure you're in the virtual environment
poetry shell

# Reinstall dependencies
poetry install
```

### Database connection errors

```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs db

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### Migration conflicts

```bash
# View current migration
alembic current

# View pending migrations
alembic history

# Manually set migration version (⚠️ use with caution)
alembic stamp head
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
poetry run uvicorn src.app.main:app --port 8001
```

---

## Useful Links

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

---

## Project Structure

```
src/app/
├── api/
│   ├── deps.py              # Shared dependencies (auth, DB)
│   └── v1/
│       ├── endpoints/       # Route handlers
│       │   ├── login.py
│       │   └── users.py
│       └── router.py        # API router
├── core/
│   ├── config.py            # Settings
│   ├── security.py          # JWT + password hashing
│   ├── logging.py           # Structured logging
│   └── exceptions.py        # Exception handlers
├── db/
│   └── session.py           # Database session
├── models/                  # SQLAlchemy models
│   └── user.py
├── repositories/            # Data access layer
│   ├── base.py
│   └── user_repository.py
├── schemas/                 # Pydantic schemas
│   ├── user.py
│   └── token.py
├── services/                # Business logic
│   └── user_service.py
└── main.py                  # FastAPI app
```

---

**Need more details?** Check:

- `README.md` - Overview and getting started
- `docs/ARCHITECTURE.md` - Design decisions
- `docs/SECURITY.md` - Security considerations
- `BITACORA.md` - Technical changelog
