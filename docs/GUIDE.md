# GUÍA DE USO: Template de API Profesional (Kitsune)

Esta guía detalla cómo utilizar este template "Kitsune" como base para crear nuevas APIs profesionales, seguras y escalables en Python.

## 📋 Stack Tecnológico

Este template utiliza las mejores prácticas modernas de Python:

- **Framework Web**: [FastAPI](https://fastapi.tiangolo.com/) (Alto rendimiento, fácil de usar, validación automática).
- **Base de Datos**: [SQLAlchemy](https://www.sqlalchemy.org/) en modo **Asíncrono** (Compatible con PostgreSQL, MySQL, SQLite).
- **Validación de Datos**: [Pydantic V2](https://docs.pydantic.dev/) (Rápido y robusto).
- **Seguridad**: Autenticación **JWT** (JSON Web Tokens) y hashing de contraseñas con **Bcrypt**.
- **Observabilidad**: Logging estructurado JSON con [Structlog](https://www.structlog.org/).
- **Testing**: [Pytest](https://docs.pytest.org/) configurado para pruebas asíncronas.
- **Infraestructura**: Docker y Docker Compose listos para producción.

---

## 🚀 Inicio Rápido (Local)

### 1. Preparar el Entorno

```bash
# Instalar Poetry (si no lo tienes)
pip install poetry

# Instalar dependencias
poetry install
```

### 2. Ejecutar la Aplicación

```bash
# Inicia el servidor de desarrollo con autoreload
poetry run uvicorn src.app.main:app --reload
```

La API estará disponible en `http://localhost:8000`.
Documentación Swagger interactiva: `http://localhost:8000/docs`.

---

## 🐳 Inicio Rápido (Docker)

Para un entorno totalmente aislado y reproducible:

```bash
# Construir y levantar servicios
docker-compose up --build
```

---

## 🔑 Características Clave

### 1. Autenticación y Seguridad

El sistema ya incluye un flujo completo de usuarios:

- **Registro**: `POST /api/v1/users/` (Crea usuario y hashea contraseña).
- **Login**: `POST /api/v1/login/access-token` (Retorna JWT).
- **Proteger Rutas**: Usa la dependencia `deps.get_current_active_user`.
  ```python
  @router.get("/secreto")
  def ruta_secreta(current_user: User = Depends(deps.get_current_active_user)):
      return {"msg": f"Hola {current_user.email}"}
  ```

### 2. Paginación Estándar

Olvídate de reinventar la rueda. Usa el esquema `Page[T]` y devolerás respuestas consistentes:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 50,
  "pages": 2
}
```

### 3. Observabilidad (Logging)

Los logs ya no son texto plano difícil de leer. El sistema genera logs estructurados ideales para herramientas como Datadog o CloudWatch.

```json
{
  "event": "request_processed",
  "method": "GET",
  "url": "/docs",
  "status": 200,
  "duration": 0.05
}
```

---

## 🛠️ Cómo Extender el Template

### Paso 1: Crear Modelo (DB)

En `src/app/models/`, crea tu archivo (ej. `producto.py`):

```python
from sqlalchemy import Column, String, Integer
from src.app.db.session import Base

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
```

_Recuerda importar tu nuevo modelo en `src/app/models/__init__.py` para que Alembic/SQLAlchemy lo detecten._

### Paso 2: Crear Esquemas (Pydantic)

En `src/app/schemas/`, define cómo se ven los datos (ej. `producto.py`):

```python
from pydantic import BaseModel

class ProductoBase(BaseModel):
    nombre: str

class Producto(ProductoBase):
    id: int
    class Config:
        from_attributes = True
```

### Paso 3: Crear Endpoint (Rutas)

En `src/app/api/v1/endpoints/`, crea la lógica (ej. `productos.py`) y regístralo en `router.py`.

### Paso 4: Crear Tests

Agrega un archivo en `tests/api/v1/test_productos.py` y usa el `client` asíncrono pre-configurado.

---

## 📁 Estructura del Proyecto

```text
├── src/
│   └── app/
│       ├── api/            # Controladores y rutas
│       ├── core/           # Configuración (Logging, Auth, Settings)
│       ├── db/             # Conexión a Base de Datos
│       ├── models/         # Modelos ORM (SQLAlchemy)
│       ├── schemas/        # Esquemas de Datos (Pydantic)
│       └── main.py         # Punto de entrada
├── tests/                  # Tests automáticos
├── Dockerfile              # Configuración de imagen Docker
├── docker-compose.yml      # Orquestación de contenedores
├── pyproject.toml          # Dependencias y configuración (Poetry)
└── poetry.lock             # Versiones exactas de dependencias
```
