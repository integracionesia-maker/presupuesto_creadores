# status.md — Control de Presupuestos (Creadores de Contenido)

- Fase: 5 (Build)
- Clasificacion: Herramienta interna — desarrollo activo
- Owner: [COMPLETAR NOMBRE] (supervision: Jose Aguilar — a confirmar)
- Semaforo: Verde
- Fecha de corte: 15/07/26
- En produccion: no

## Estado

Backend (FastAPI) y frontend (Vite + React + ApexCharts) funcionando localmente. Bug critico de React duplicado ("Invalid hook call") corregido — causado por un alias manual mal configurado en `vite.config.js`. Dashboard con filtro de fechas, 7 KPI cards y 4 graficos ApexCharts renderizando sin errores de consola (verificado con Playwright headless). Datos duplicados de creadores/marcas (por variantes con/sin acento) fusionados sin perder historial de tickets.

## Bloqueo principal

Ninguno activo. Gaps estructurales pendientes (no bloquean el uso, si el crecimiento): sin git, sin autenticacion, sin tests.

## Siguiente accion

Inicializar control de versiones (git) — es el gap mas urgente dado que hoy no hay forma de revertir cambios ni ver historial real.

## Stack

FastAPI + SQLAlchemy + SQLite (backend) · Vite 6 + React 18.3.1 + Tailwind 3 + ApexCharts (frontend)
Deploy: ninguno — local `127.0.0.1:8000` (backend) / `127.0.0.1:5173` (frontend)

## Metricas tecnicas

| Metrica | Valor |
|---|---|
| % MVP | ver MVP_BREAKDOWN.md |
| Creadores activos | 6 (sin duplicados, tras fusion 2026-07-15) |
| Marcas activas | 8 (sin duplicados, tras fusion 2026-07-15) |
| Tickets totales | 89 |
| Historial de datos | 12 meses (Ago 2025 - Jul 2026) |
| Tests | 0 |
| Control de versiones | No (pendiente inicializar git) |

## Metricas de impacto

| Metrica | Antes (2026-07-15, inicio de sesion) | Despues |
|---|---|---|
| Consola del navegador | Error fatal — dashboard en blanco | 0 errores, 4 graficos visibles |
| Creadores/marcas | 9 creadores / 9 marcas (con duplicados por acento) | 6 creadores / 8 marcas (fusionados) |
| KPI "Marcas Activas" | Mostraba 89 (bug: contaba filas de JOIN) | Muestra 8 (correcto) |
| Historial de datos | ~2 meses | 12 meses |

## Seguridad

Sin checklist formal todavia (ver `RISKS.md`). Gaps conocidos: sin autenticacion en la API, sin backups de `presupuesto.db`, sin control de versiones.

## KPI History

| Semana | Semaforo | Bloqueo |
|---|---|---|
| Sem 29 (15 Jul 2026) | Verde | ninguno |
