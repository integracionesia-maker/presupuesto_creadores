# Control de Presupuestos — Creadores de Contenido — Grupo Ortiz

> Conexiones pool: [[CLAUDE]] | [[context_proyectos]] | [[framework_operative_enforcement/CLAUDE]] | [[framework_operative_enforcement/PLAYBOOK]] | [[framework_operative_enforcement/FRAMEWORK]]
> Recursos compartidos: [[IDENTIDAD DE MARCA/context_design]] (visual)
> Archivos del proyecto: [[CLAUDE]] | [[context]] | [[status]] | [[BACKLOG]] | [[RISKS]] | [[MVP_BREAKDOWN]] | [[DESIGN_SYSTEM]] | [[avances_diarios]]

## Stack

Backend: Python · FastAPI · SQLAlchemy · SQLite (`backend/presupuesto.db`)
Frontend: Vite 6 · React 18.3.1 · Tailwind 3 · ApexCharts (`apexcharts` + `react-apexcharts`)

Backend: `PYTHONPATH=backend python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` (ejecutar **desde** `backend/` — rutas de DB y uploads son relativas al cwd)
Frontend: `npm install && npx vite --host 127.0.0.1 --port 5173`

## Reglas criticas

- **Sin control de versiones todavia** — la carpeta no es un repo git. No asumir que `git status`/commits reflejan el estado real hasta que se inicialice (ver RISKS.md #1).
- **Sin autenticacion** — el backend no valida usuarios ni roles. No exponer fuera de `127.0.0.1` sin agregar auth primero (ver RISKS.md #2).
- Rutas de `backend/app/main.py` y `database.py` son relativas al cwd (`./presupuesto.db`, `./uploads`) — siempre levantar uvicorn con cwd = `backend/`.
- No agregar alias manuales de `react`/`react-dom` en `vite.config.js` — causo el bug de "Invalid hook call" (resuelto 2026-07-15). `resolve.dedupe` + `optimizeDeps.include` es suficiente con un solo `node_modules`.
- En `apexTheme.js`/`createApexOptions`, nunca asignar `stroke`/`fill`/`plotOptions`/`responsive` como `undefined` explicito — ApexCharts 5.x pisa sus defaults internos y truena el dashboard completo sin error boundary.
- Datos de creadores/marcas: evitar duplicados por acentos al re-seedear (`seed.py` ya usa ortografia con acento — no revertir a versiones sin acento).

## Design system

Fuente de verdad: `IDENTIDAD DE MARCA/context_design.md` (repo `context_desing_go`).
Naranja GO `#FB670B` + neutros `#262626` `#535353` `#C5C5C5` `#ECEBE0` `#FFFFFF` ya aplicados en `tailwind.config.js`.
Tipografia actual: Space Grotesk (display) + Inter (body) + JetBrains Mono — **no** son las fuentes oficiales de marca (Blauer Nue / Conthic); pendiente decidir si se formaliza el cambio (ver DESIGN_SYSTEM.md).

## Deploy

No desplegado — corre local en `127.0.0.1:8000` (backend) y `127.0.0.1:5173` (frontend). Sin entorno de produccion todavia.
