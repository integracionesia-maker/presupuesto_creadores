# BACKLOG — Control de Presupuestos (Creadores de Contenido)

> App interna de control de presupuestos para creadores de contenido de Grupo Ortiz. Desarrollo activo, sin deploy.

---

## Pendientes

| # | Tarea | Fase | Prioridad | Owner | Estado |
|---|---|---|---|---|---|
| 1 | Inicializar repo git (sin control de versiones hoy) | 5 | Alta | — | Pendiente |
| 2 | Autenticacion / control de acceso en la API | 5 | Alta | — | Pendiente |
| 3 | Backups automaticos de `presupuesto.db` | 5 | Media | — | Pendiente |
| 4 | Tests automatizados (backend: CRUD + calculo de presupuesto) | 6 | Media | — | Pendiente |
| 5 | Crear `SECURITY.md` con checklist formal | 6 | Media | — | Pendiente |
| 6 | Confirmar owner real del proyecto y actualizar `context.md`/`status.md` | 5 | Alta | — | Pendiente |
| 7 | Decidir si se formaliza tipografia de marca (Blauer Nue/Conthic) o se mantiene Space Grotesk/Inter | 5 | Baja | — | Pendiente |
| 8 | Definir plan de deploy (entorno accesible para el equipo) | 7 | Media | — | Pendiente |
| 9 | Revisar duplicado de `puppeteer` en `package.json` raiz (no parece pertenecer a este proyecto) | 5 | Baja | — | Pendiente |

## En progreso

_Ninguna tarea en progreso registrada al 15/07/2026._

## Completados (recientes)

| # | Tarea | Fase | Completado | Evidencia |
|---|---|---|---|---|
| 1 | Fix bug "Invalid hook call" (React duplicado por alias en vite.config.js) | 5 | 15 Jul 2026 | `vite.config.js` — alias manual eliminado |
| 2 | Fix crash de ApexCharts por claves `undefined` en `createApexOptions` | 5 | 15 Jul 2026 | `charts/apexTheme.js` |
| 3 | Poblado de 12 meses de historial de tickets | 5 | 15 Jul 2026 | `backend/seed_more_months.py` — 78 tickets nuevos |
| 4 | Fusion de creadores/marcas duplicados (variantes con/sin acento) | 5 | 15 Jul 2026 | `backend/merge_duplicates.py` |
| 5 | Correccion de sobregiro post-fusion (3 creadores quedaron con presupuesto negativo) | 5 | 15 Jul 2026 | `backend/trim_overbudget.py` |
| 6 | Fix bug KPI "Marcas Activas" (contaba filas de JOIN, no marcas distintas) | 5 | 15 Jul 2026 | `backend/app/crud.py::get_dashboard_summary` |
| 7 | Correccion de `seed.py` para usar nombres acentuados (evita duplicados en futuro reseed) | 5 | 15 Jul 2026 | `backend/seed.py` |
| 8 | Verificacion end-to-end con Playwright (0 errores de consola, 4 graficos visibles) | 5 | 15 Jul 2026 | Screenshots + `page.on('pageerror')` sin resultados |
