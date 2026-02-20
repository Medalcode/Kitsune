# Skills

Resumen
-------

En el contexto de Kitsune, una `skill` es una unidad de capacidad reutilizable que encapsula una operación de negocio concreta y probada. Las `skills` están diseñadas para ser pequeñas, fáciles de testear y composables por los `agents` u otros servicios.

Qué es una `skill`
-------------------

- Unidad lógica que expone un contrato claro (inputs, outputs, errores).
- Debe ser fácil de ejecutar en tests unitarios y de integración.
- Debe ser desacoplada de detalles de transporte (cola, HTTP) y de infraestructura donde sea posible.

Contratos y API interna
------------------------

- Inputs: definir tipos y validación (usar Pydantic / esquemas compartidos cuando corresponda).
- Outputs: normalizar forma de salida y errores; documentar códigos de error esperados.
- Errores: preferir excepciones específicas y serializables para que los agents o llamantes puedan reaccionar.

Buenas prácticas de diseño
-------------------------

- Idempotencia: diseñar `skills` para que puedan reintentarse si es relevante.
- Efectos laterales: minimizar efectos laterales o aislarlos en pasos concretos.
- Dependencias: inyectar dependencias (repositorios, clientes) para facilitar pruebas.
- Cohesión: una `skill` debería hacer una sola cosa bien.

Composición y versionado
------------------------

- Composición: los `agents` u otras `skills` pueden componer varias `skills` para construir flujos de negocio.
- Versionado: versionar la interfaz de una `skill` cuando cambies contractos; mantener compatibilidad hacia atrás cuando sea posible.

Pruebas y validación
---------------------

- Unit tests: probar la `skill` aislada con mocks para dependencias (repositorios, clientes HTTP).
- Integration tests: probar con infra real o con doubles (p. ej. Redis en memory, base de datos de pruebas).
- Property-based tests/contratos: cuando aplique, asegurar invariantes importantes (p. ej. idempotencia).

Ejemplos y mapping a código existente
-------------------------------------

- Servicios actuales (ej.: `src/app/services/user_service.py`) pueden contener operaciones que se conviertan en `skills` reutilizables.
- Repositorios (`src/app/repositories/*`) se inyectan en las `skills` para acceso a datos.

Guía rápida para crear una `skill`
---------------------------------

1. Definir el contrato (Pydantic schema para input/output).
2. Implementar la lógica en un módulo `src/app/skills/<nombre>_skill.py` o en `src/app/services` con una API clara.
3. Añadir unit tests y documentar ejemplos de uso.
4. Consumir la `skill` desde un agent o endpoint según corresponda.

Checklist mínimo antes de merge
-------------------------------

- [ ] Contrato documentado en `docs/skills.md`.
- [ ] Unit tests con cobertura para los caminos felices y errores.
- [ ] Ejemplo de consumo (en tests o en `docs/dev_notes/`).

Lecturas relacionadas
---------------------

- `docs/agents.md` — cómo los agents orquestan `skills`.
- `src/app/services/user_service.py` — ejemplo de operación que puede mapear a una `skill`.

Evolución
---------

En futuros pasos podemos extraer ejemplos concretos en `src/app/skills/` y añadir un pequeño scaffolding y tests de integración en `tests/`.
