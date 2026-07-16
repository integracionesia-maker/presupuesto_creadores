# RISKS — Control de Presupuestos (Creadores de Contenido)

> Registro de riesgos activos y cerrados del sistema.

---

## Activos

| # | Riesgo | Severidad | Fecha | Impacto | Mitigacion |
|---|---|---|---|---|---|
| 1 | Sin control de versiones — la carpeta no es un repo git | Alto | 2026-07-15 | Sin historial, sin forma de revertir cambios, riesgo de perdida de trabajo | Inicializar `git init` + primer commit; ver BACKLOG #1 |
| 2 | Sin autenticacion en la API (`main.py` solo tiene CORS, sin login/roles) | Alto | 2026-07-15 | Cualquiera con acceso a la red local puede leer/modificar/borrar presupuestos y tickets | Agregar auth antes de exponer fuera de `127.0.0.1`; ver BACKLOG #2 |
| 3 | Sin backups de `presupuesto.db` (SQLite es un solo archivo) | Medio | 2026-07-15 | Corrupcion de disco o borrado accidental = perdida total de datos | Script de backup diario simple; ver BACKLOG #3 |
| 4 | Sin tests automatizados | Medio | 2026-07-15 | Cambios pueden romper el calculo de presupuestos sin detectarse — ya casi ocurre hoy al fusionar duplicados (ver "Cerrados" #3, casi genera datos financieros negativos sin ningun test que lo detectara) | Tests basicos de CRUD + calculo de presupuesto; ver BACKLOG #4 |
| 5 | Owner del proyecto no confirmado en la documentacion | Bajo | 2026-07-15 | Ambiguedad sobre quien decide prioridades y responde bloqueos | Confirmar y actualizar `context.md`/`status.md`; ver BACKLOG #6 |
| 6 | Tipografia de marca no formalizada (usa Space Grotesk/Inter en vez de Blauer Nue/Conthic) | Bajo | 2026-07-15 | Inconsistencia visual leve con el resto del portafolio GO | Decidir con direccion si se adopta la tipografia oficial; ver BACKLOG #7 |

## Cerrados

| # | Riesgo | Fecha cerrado | Como se resolvio |
|---|---|---|---|
| 1 | Dashboard roto por error "Invalid hook call" (React duplicado) | 2026-07-15 | Alias manual de `react`/`react-dom` en `vite.config.js` eliminado; `resolve.dedupe` + `optimizeDeps.include` es suficiente |
| 2 | Dashboard completo crasheaba (pantalla en blanco) al agregar graficos ApexCharts | 2026-07-15 | `createApexOptions` ya no asigna `stroke`/`fill`/`plotOptions`/`responsive` como `undefined` explicito |
| 3 | Creadores/marcas duplicados por variantes con/sin acento generaron sobregiro (3 creadores con presupuesto negativo tras fusion) | 2026-07-15 | Tickets de relleno mas grandes recortados hasta volver a presupuesto positivo; `seed.py` corregido para no reintroducir el duplicado |
| 4 | KPI "Marcas Activas" mostraba 89 en vez de 8 (contaba filas del JOIN, no marcas distintas) | 2026-07-15 | `func.count(func.distinct(models.Brand.id))` + `join` en vez de `outerjoin` sin agrupar |
| 5 | Procesos backend "zombie" (workers huerfanos) servian codigo desactualizado tras reinicios | 2026-07-15 | Identificados y eliminados via `Get-CimInstance Win32_Process` (parent_pid muerto); backend reiniciado limpio |

## Top 3 para direccion

1. Sin control de versiones — riesgo mas urgente, cero costo resolverlo
2. Sin autenticacion — bloqueante si el proyecto crece mas alla de uso interno de una sola persona
3. Owner no confirmado — necesario para que este seguimiento tenga sentido hacia adelante
