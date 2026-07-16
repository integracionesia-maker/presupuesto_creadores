# Control de Presupuestos — Creadores de Contenido — Grupo Ortiz

> Conexiones pool: [[CLAUDE]] | [[context_proyectos]] | [[framework_operative_enforcement/CLAUDE]] | [[framework_operative_enforcement/PLAYBOOK]] | [[framework_operative_enforcement/FRAMEWORK]]
> Recursos compartidos: [[IDENTIDAD DE MARCA/context_design]] (visual)
> Archivos del proyecto: [[CLAUDE]] | [[context]] | [[status]] | [[BACKLOG]] | [[RISKS]] | [[MVP_BREAKDOWN]] | [[DESIGN_SYSTEM]] | [[avances_diarios]] | [[doc/auth-arquitectura]] | [[doc/auth-manual-usuario]]

## Stack

Backend: Python · FastAPI · SQLAlchemy · SQLite (`backend/presupuesto.db`)
Frontend: Vite 6 · React 18.3.1 · Tailwind 3 · ApexCharts (`apexcharts` + `react-apexcharts`)

Backend: `JWT_SECRET_KEY=<ver .env.example> PYTHONPATH=backend python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` (ejecutar **desde** `backend/` — rutas de DB y uploads son relativas al cwd; `JWT_SECRET_KEY` es obligatorio, el proceso no arranca sin él)
Frontend: `npm install && npx vite --host 127.0.0.1 --port 5173`

Primer arranque (o para crear el superadmin si no existe): desde `backend/`, `python seed_auth.py` — ver sección "Autenticación" abajo.

## Reglas criticas

- **Sin control de versiones todavia** — la carpeta no es un repo git. No asumir que `git status`/commits reflejan el estado real hasta que se inicialice (ver RISKS.md #1).
- **Autenticacion obligatoria** — todos los endpoints (excepto `/api/health` y `/api/auth/login`) requieren sesión; los roles son `superadmin`/`admin`/`creador` (ver `doc/auth-arquitectura.md`). La regla anterior de "sin autenticación, no exponer fuera de 127.0.0.1" ya no aplica tal cual — pero sigue sin haber HTTPS/CSP/HSTS, así que no exponer fuera de `127.0.0.1` sin agregar eso primero (ver RISKS.md #2 residual).
- La cuenta `superadmin` es **inmutable por API** (ningún endpoint cambia su rol ni la desactiva) — si se pierde su contraseña, usar `backend/reset_superadmin_password.py` (acceso al servidor, no a la app).
- Rutas de `backend/app/main.py` y `database.py` son relativas al cwd (`./presupuesto.db`, `./uploads`) — siempre levantar uvicorn con cwd = `backend/`.
- No agregar alias manuales de `react`/`react-dom` en `vite.config.js` — causo el bug de "Invalid hook call" (resuelto 2026-07-15). `resolve.dedupe` + `optimizeDeps.include` es suficiente con un solo `node_modules`.
- En `apexTheme.js`/`createApexOptions`, nunca asignar `stroke`/`fill`/`plotOptions`/`responsive` como `undefined` explicito — ApexCharts 5.x pisa sus defaults internos y truena el dashboard completo sin error boundary.
- Datos de creadores/marcas: evitar duplicados por acentos al re-seedear (`seed.py` ya usa ortografia con acento — no revertir a versiones sin acento).

## Design system

Fuente de verdad: `IDENTIDAD DE MARCA/context_design.md` (repo `context_desing_go`).
Naranja GO `#FB670B` + neutros `#262626` `#535353` `#C5C5C5` `#ECEBE0` `#FFFFFF` ya aplicados en `tailwind.config.js`.
Tipografia actual: Space Grotesk (display) + Inter (body) + JetBrains Mono — **no** son las fuentes oficiales de marca (Blauer Nue / Conthic); pendiente decidir si se formaliza el cambio (ver DESIGN_SYSTEM.md).

## Autenticación

Diseño completo y matriz de permisos: `doc/auth-arquitectura.md`. Manual por rol: `doc/auth-manual-usuario.md`.

Variables de entorno nuevas (ver `.env.example`): `JWT_SECRET_KEY` (obligatoria, generar con `python -c "import secrets; print(secrets.token_hex(32))"`), `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, `JWT_REFRESH_TOKEN_EXPIRE_DAYS`, `ENV` (`development`/`production`, controla `Secure` en cookies y si `/docs`/`/redoc` quedan expuestos), `SUPERADMIN_USERNAME`/`SUPERADMIN_EMAIL`/`SUPERADMIN_PASSWORD` (solo para `seed_auth.py`).

Pruebas: `cd backend && python -m pytest` (90 pruebas, DB de prueba propia). E2E: ver `doc/auth-manual-usuario.md` §Pruebas.

## Deploy

No desplegado — corre local en `127.0.0.1:8000` (backend) y `127.0.0.1:5173` (frontend). Sin entorno de produccion todavia. Antes de exponer fuera de `127.0.0.1`: agregar HTTPS (obligatorio para `Secure` en cookies), CSP/HSTS, y revisar `CORS_ORIGINS` (ver RISKS.md #2 residual y `doc/auth-arquitectura.md` §6).
