# Agents

Resumen
-------

En este proyecto, un "agent" es un componente en tiempo de ejecución responsable de ejecutar tareas autónomas y orquestadas fuera del ciclo de petición-respuesta HTTP. Los agents están pensados para encargarse de trabajo asíncrono, coordinación de procesos, integración con colas/colas de mensajes, y tareas programadas o de largo recorrido.

Contexto y alcance
------------------

- Audiencia: desarrolladores que implementan arquitecturas asíncronas en Kitsune.
- Alcance: definición conceptual y pautas de diseño. No contiene implementación completa, pero apunta a los lugares del código donde integrar agents (`src/app/services`, `src/app/repositories`, `src/app/api`).

Responsabilidades típicas
------------------------

- Orquestación de tareas compuestas (ej. flujos que llaman a varios `skills`).
- Ejecutar trabajos en background (workers) y jobs programados (schedulers).
- Reintentos, backoff y manejo de errores cronológicos (DLQs cuando aplique).
- Observabilidad: métricas, trazas distribuidas y logs estructurados.
- Salud y lifecycle: endpoints de health checks, readiness, y graceful shutdown.

Tipos de agents
---------------

- Worker: consume mensajes de una cola y procesa unidades de trabajo.
- Scheduler: dispara tareas en intervalos o en momentos concretos.
- Orchestrator: coordina llamadas a múltiples `skills` para completar un flujo de negocio.
- Adapter: integra sistemas externos (APIs, colas, servicios externos).

Integración con la aplicación (patrón recomendado)
-------------------------------------------------

1. Separar responsabilidades: la lógica de negocio permanece en `services` y `skills` (ver `docs/skills.md`). El agent debe orquestar pero no contener lógica de negocio pesada.
2. Acceso a datos a través de `repositories` (ej.: `src/app/repositories/user_repository.py`).
3. Cuando el agent necesita exponer control, añadir endpoints en `src/app/api` que interactúen con él mediante un canal seguro (p. ej. jobs encolados, llamadas a API interna).

Referencias de código
---------------------

- Servicios: [src/app/services](src/app/services)
- Repositorios: [src/app/repositories](src/app/repositories)
- Endpoints: [src/app/api](src/app/api)

Patrones de diseño y recomendaciones
-----------------------------------

- Idempotencia: diseñar tareas para que puedan reintentarse sin efectos adversos.
- Retries y backoff exponencial: preferir bibliotecas probadas (por ejemplo, Celery, RQ, o soluciones basadas en Redis + workers custom si no se desea completar un framework).
- Timeouts y circuit breakers: proteger llamadas a servicios externos.
- Observabilidad: emitir métricas por tarea (latencia, éxito/fracaso, reintentos) y puentear trazas (distributed tracing).
- Seguridad: los agents deben usar las mismas políticas de credenciales que la app (no embebas secretos en código).

Operaciones y despliegue
------------------------

- Supervisión: exponer métricas Prometheus y /health para readiness.
- Escalado: diseñar agents para ser horizontales (stateless o con estado externo en Redis/Postgres).
- Migraciones: coordinar despliegues con migraciones de base de datos (Alembic) cuando las tareas dependan de nuevos esquemas.

Cuándo usar un agent vs una llamada HTTP directa
-------------------------------------------------

- Usar agent cuando la tarea: es de larga duración; requiere reintento/cola; necesita ser desacoplada para resiliencia; o cuando debe ser procesada por lotes.
- Usar llamada HTTP directa cuando la operación es rápida, crítica para la latencia de la petición y no tolera desacoplamiento.

Checklist básico para pasar de diseño → implementación
------------------------------------------------------

- [ ] Definir contractos (qué inputs/outputs) y límites de timeout.
- [ ] Seleccionar mecanismo de transporte (cola, Redis, Pub/Sub, DB-backed queue).
- [ ] Implementar agente mínimo con logging y métricas.
- [ ] Añadir pruebas de integración que simulen la cola y fallos.
- [ ] Actualizar CI para ejecutar pruebas y validar health checks.

Lecturas relacionadas
---------------------

- [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/dev_notes/implementation_plan.md](dev_notes/implementation_plan.md)

Evolución
---------

Este documento es conceptual. Para una guía de implementación paso a paso o ejemplo mínimo (scaffolding), añadir un documento en `docs/dev_notes/` o un ejemplo en `src/app/agents/example_agent.py`.
