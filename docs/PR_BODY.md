Título: docs: añadir guías `agents` y `skills`

Resumen:
- Se añaden las páginas conceptuales `docs/agents.md` y `docs/skills.md` con definiciones, responsabilidades, patrones de diseño y checklist para pasar de diseño a implementación.

Motivación:
- Documentar una estrategia escalable y profesional para orquestación de tareas asíncronas (`agents`) y capacidades reutilizables (`skills`) en el template Kitsune.

Qué incluye este PR:
- `docs/agents.md` — guía conceptual sobre agents: tipos, responsabilidades, integración, despliegue y checklist de implementación.
- `docs/skills.md` — guía conceptual sobre skills: contratos, buenas prácticas, pruebas y checklist mínimo.
- Actualización breve en `README.md` para enlazar las nuevas páginas.

Notas para reviewers:
- Los documentos son conceptuales: si se desea, puedo añadir scaffolding mínimo en `src/app/agents/` y ejemplos en `tests/` en un PR aparte.
- Idioma: español. Si prefieren inglés, puedo crear equivalentes en inglés.

Checklist antes merge:
- [ ] Revisar links y referencias a archivos existentes.
- [ ] Confirmar idioma y alcance.
- [ ] (Opcional) Añadir ejemplo mínimo de agent + tests en PR separado.
