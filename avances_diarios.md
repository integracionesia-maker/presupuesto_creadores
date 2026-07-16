# Avances Diarios — Control de Presupuestos (Creadores de Contenido)

> Owner: [COMPLETAR NOMBRE]
> Inicio de seguimiento: 2026-07-15

---

## Semana 29 — Julio 2026

### MIE 15/07 — Debug critico + poblado de datos + fusion de duplicados + setup de framework

**Que hice:**
- Diagnostique y corregi el error fatal "Invalid hook call" / React duplicado en el frontend — causado por un alias manual de `react`/`react-dom` en `vite.config.js` que rompia la resolucion de modulos de Vite (no habia ninguna copia duplicada real de React en disco)
- Reinstale `node_modules` limpio, mate procesos zombie en puertos 5173/8000, levante backend y frontend correctamente (el comando documentado de arranque del backend asumia el cwd incorrecto)
- Instale Playwright + Chromium para verificar el dashboard en un navegador real (no habia herramienta de browser disponible) — confirme 0 errores de consola
- Encontre y corregi un segundo bug real: `createApexOptions` asignaba `undefined` explicito a `stroke`/`fill`/`plotOptions`/`responsive`, lo que rompia los defaults internos de ApexCharts 5.x y crasheaba el dashboard completo (pantalla en blanco, sin error boundary)
- Genere 78 tickets adicionales distribuidos en 12 meses de historial (`seed_more_months.py`) para poblar el dashboard con datos representativos
- Detecte y fusione creadores/marcas duplicados por variantes con/sin acento (Mariana Lopez/López, Diego Fernandez/Fernández, Sofia/Sofía Herrera, L'Oreal/L'Oréal) — reasigne tickets al registro canonico y corregi `seed.py` para no reintroducir el duplicado en un futuro reseed
- La fusion dejo 3 creadores con presupuesto negativo (cada duplicado habia acumulado gasto por separado contra el mismo presupuesto); recorte los tickets de relleno mas grandes hasta volver a presupuesto positivo, con confirmacion del usuario sobre el criterio a aplicar
- Encontre y corregi un bug preexistente en el backend: el KPI "Marcas Activas" mostraba 89 (contaba filas del JOIN) en vez de 8 (marcas distintas reales)
- Identifique y elimine procesos backend "zombie" (workers huerfanos que sobrevivian a la muerte de su proceso padre y seguian sirviendo codigo desactualizado)

**Evidencia:**
- `vite.config.js` — alias manual eliminado
- `frontend/src/components/charts/apexTheme.js` — claves opcionales condicionales
- `backend/seed_more_months.py`, `merge_duplicates.py`, `trim_overbudget.py` — scripts de datos
- `backend/app/crud.py::get_dashboard_summary` — fix `func.distinct`
- Screenshots Playwright (dashboard completo, 4 graficos, 0 errores de consola)
- `GET /api/dashboard/summary` → `active_brands: 8` (antes: 89)

**MVP:** 67% (8/12 entregables — ver `MVP_BREAKDOWN.md`)

**Bloqueo:** ninguno

**Siguiente:** inicializar git (repo sin control de versiones hoy es el gap mas urgente)

**Semaforo:** Verde

---

## Historial de semaforos

| Semana | Semaforo | Bloqueo principal |
|---|---|---|
| Sem 29 (15 Jul 2026) | Verde | ninguno |
