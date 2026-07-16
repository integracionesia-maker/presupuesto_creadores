# MVP Breakdown — Control de Presupuestos (Creadores de Contenido)

> Formula: `% MVP = completados / total * 100`
> Nota: desglose inferido del estado real del codigo (2026-07-15) — el owner debe validar/ajustar el alcance formal del MVP.

---

| # | Entregable | Descripcion | Estado | Evidencia |
|---|---|---|---|---|
| 1 | CRUD creadores/marcas | Alta, listado, edicion de creadores y marcas | Hecho | `backend/app/routers/creators.py`, `brands.py` |
| 2 | Tickets con comprobante | Registro de gasto + archivo (PNG/JPG/PDF) por creador y marca | Hecho | `backend/app/routers/tickets.py`, `UploadTicketModal.jsx` |
| 3 | Calculo de presupuesto | `spent_budget`/`remaining_budget` recalculado por ticket | Hecho | `backend/app/crud.py` |
| 4 | Dashboard analytics API | Endpoints summary/monthly-spend/creator-usage/brand-spend | Hecho | `backend/app/routers/dashboard.py` |
| 5 | Dashboard frontend | Filtro de fechas + presets + 7 KPI cards | Hecho | `Dashboard.jsx`, `DateRangeFilter.jsx` |
| 6 | Graficos ApexCharts | 4 graficos tema oscuro (mensual, por marca, por creador, tendencia) | Hecho | `components/charts/*.jsx` — verificado sin errores de consola (Playwright, 2026-07-15) |
| 7 | Listados auxiliares | Vista de creadores y tabla de transacciones | Hecho | `CreatorList.jsx`, `TransactionTable.jsx` |
| 8 | Datos limpios de prueba | 12 meses de historial, sin creadores/marcas duplicados | Hecho | 89 tickets, 6 creadores, 8 marcas (2026-07-15) |
| 9 | Control de versiones | Repo git inicializado con historial real | Pendiente | — |
| 10 | Autenticacion | Login/roles antes de exponer fuera de localhost | Pendiente | — |
| 11 | Tests automatizados | Cobertura minima backend (CRUD + calculo presupuesto) | Pendiente | — |
| 12 | Deploy | Entorno accesible por el equipo (hoy solo `127.0.0.1`) | Pendiente | — |

- **Completados:** 8 de 12
- **% MVP real:** 67%
- **Ultimo cerrado:** #8 Datos limpios de prueba — 15 Jul 2026
- **Siguiente:** #9 Control de versiones (git)

**Definition of Done:** codigo funciona + tests pasan + evidencia en avances_diarios.md + owner confirma.
