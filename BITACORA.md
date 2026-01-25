# 📔 Bitácora del Proyecto Kitsune

Registro de cambios, mejoras implementadas y tareas pendientes para la evolución del proyecto.

## ✅ Tareas Realizadas

### Fase 1: Modernización y DevOps

- [x] **Gestión de Dependencias**: Migración completa de `requirements.txt` a **Poetry**.
- [x] **Docker**:
  - Optimización de imágenes (Multi-stage build).
  - Implementación de usuario no-root (`appuser`) por seguridad.
- [x] **CI/CD**: Actualización de GitHub Actions para usar Poetry y validar tests/linting.
- [x] **Documentación**: Consolidación de guías en `docs/` y actualización del README.

### Fase 2: Arquitectura Escalable

- [x] **Patrón Repositorio**:
  - Creación de `BaseRepository` genérico.
  - Implementación de `UserRepository` para abstraer consultas de usuarios.
  - Refactorización de `UserService` para usar repositorios en lugar de sesiones de DB directas.
- [x] **Base de Datos**: Migración de configuración por defecto de SQLite a **PostgreSQL**.
- [x] **Infraestructura**:
  - Inclusión de **Redis** en `docker-compose.yml` y configuración.
  - Configuración de drivers asíncronos (`asyncpg`).

## 🚀 Tareas Pendientes (Roadmap)

### Escalabilidad & Performance

- [ ] **Implementar Caché**: Usar Redis para cachear respuestas de endpoints frecuentes.
- [ ] **Rate Limiting**: Configurar limitación de peticiones (Throttling) usando Redis.
- [ ] **Background Tasks**: Integrar **Celery** o **Arq** para tareas pesadas (emails, procesamiento).

### Seguridad & Calidad

- [ ] **Tests de Integración con DB**: Configurar CI para levantar servicios Postgres de prueba.
- [ ] **Auditoría de Seguridad**: Revisar headers de seguridad y configuración de CORS para producción.

### Funcionalidad

- [ ] **Recuperación de Contraseña**: Implementar flujo de "Olvidé mi contraseña" (Email + Token).
- [ ] **Gestión de Roles**: Añadir tabla de roles y permisos granulares.
