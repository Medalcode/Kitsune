# Kitsune API Template

A professional, production-ready implementation of a FastAPI application.

## Features

- **FastAPI**: Modern Python web framework.
- **SQLAlchemy (Async)**: Database interaction using modern async patterns.
- **Security**:
  - JWT Authentication (OAuth2 with Password Flow).
  - Password hashing using Bcrypt.
  - Role-based interaction (Users must be authenticated).
- **CORS Configured**: Ready for frontend integration.
- **Dockerized**: Ready for deployment.

> 📘 **Documentation**:
>
> - [Full User Guide](docs/GUIDE.md)
> - [Development Notes](docs/dev_notes/)
> - [📔 Bitácora de Cambios](BITACORA.md)

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (optional)

### Local Setup

1. **Install Dependencies**:

   ```bash
   poetry install
   ```

2. **Run the Application**:

   ```bash
   poetry run uvicorn src.app.main:app --reload
   ```

3. **Explore the API**:
   Open [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive Swagger documentation.

## Authentication Flow

1. **Create User**: `POST /api/v1/users/` with email and password.
2. **Login**: `POST /api/v1/login/access-token` to get a JWT.
3. **Access Protected Routes**: Use the JWT in the `Authorization: Bearer <token>` header.

## Folder Structure

- `src/app/api`: API Endpoints and Routers.
- `src/app/core`: Configuration and Security settings.
- `src/app/db`: Database connection and session management.
- `src/app/models`: SQLAlchemy ORM models.
- `src/app/schemas`: Pydantic schemas for validation.
