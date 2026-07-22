# Control de Presupuestos — Creadores de Contenido — Grupo Ortiz

> Conexiones pool: [[CLAUDE]] | [[context_proyectos]] | [[framework_operative_enforcement/CLAUDE]] | [[framework_operative_enforcement/PLAYBOOK]] | [[framework_operative_enforcement/FRAMEWORK]]
> Recursos compartidos: [[IDENTIDAD DE MARCA/context_design]] (visual)
> Archivos del proyecto: [[CLAUDE]] | [[context]] | [[status]] | [[BACKLOG]] | [[RISKS]] | [[MVP_BREAKDOWN]] | [[DESIGN_SYSTEM]] | [[avances_diarios]] | [[doc/auth-arquitectura]] | [[doc/auth-manual-usuario]] | [[doc/presupuestos-y-validacion]] | [[doc/gastos-generales-manual]] | [[doc/borrado-tickets]]

## Stack

Backend: Python · FastAPI · SQLAlchemy · SQLite (`backend/presupuesto.db`)
Frontend: Vite 6 · React 18.3.1 · Tailwind 3 · ApexCharts (`apexcharts` + `react-apexcharts`)

Backend: `JWT_SECRET_KEY=<ver .env.example> PYTHONPATH=backend python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` (ejecutar **desde** `backend/` — rutas de DB y uploads son relativas al cwd; `JWT_SECRET_KEY` es obligatorio, el proceso no arranca sin él)
Frontend: `npm install && npx vite --host 127.0.0.1 --port 5173`

Primer arranque (o para crear el superadmin si no existe): desde `backend/`, `python seed_auth.py` — ver sección "Autenticación" abajo.

## Reglas criticas

- **Repo git ya inicializado** — rama principal `master`, se trabaja en `dami-branch` (commitear solo ahí; integrar a `master` solo cuando el usuario lo pida explícitamente).
- **Autenticacion obligatoria** — todos los endpoints (excepto `/api/health` y `/api/auth/login`) requieren sesión; los roles son `superadmin`/`admin`/`creador` (ver `doc/auth-arquitectura.md`). Sigue sin haber HTTPS/CSP/HSTS, así que no exponer fuera de `127.0.0.1` sin agregar eso primero (ver RISKS.md #2 residual).
- **Gestión de usuarios es exclusiva de `superadmin`** (R4) — un `admin` ya no gestiona usuarios en absoluto (ni siquiera los de rol `creador`), recibe 403 en todo `/api/users/*`. Sí gestiona creadores, marcas, ciclos de presupuesto y validación de tickets.
- La cuenta `superadmin` es **inmutable por API** (ningún endpoint cambia su rol ni la desactiva) — si se pierde su contraseña, usar `backend/reset_superadmin_password.py` (acceso al servidor, no a la app).
- **Ciclos de presupuesto (semanal/mensual) nunca bloquean por fondos insuficientes** — aprobar un ticket puede dejar el ciclo en negativo a propósito (decisión explícita del usuario); no agregar validación de fondos en `crud.approve_ticket`/`create_ticket`. Un ticket se asigna a su ciclo por la fecha en que se **sube**, no la fecha en que se aprueba — ese campo (`budget_cycle_id`) se fija una sola vez al crear el ticket y nunca se recalcula. Detalle completo: `doc/presupuestos-y-validacion.md`.
- **Estados de ticket**: `pendiente → aprobado | rechazado` (terminales). Solo los tickets subidos por un `creador` nacen `pendiente`; los de `admin`/`superadmin` se auto-aprueban. Un ticket `pendiente` nunca descuenta del ciclo; uno `rechazado` tampoco (nunca).
- **Borrado de tickets (lógico y físico, R12)** — exclusivo de `admin`/`superadmin`. Un ticket con `is_deleted=True` deja de contar para TODO cálculo (listados, dashboard, brand-spend, cola de validación) — el filtro `is_deleted == False` debe estar en **todas** las queries de `tickets` sin excepción. Si el ticket borrado estaba `aprobado`, se revierte su monto del ciclo con `max(0, cycle.spent - amount)` (nunca negativo). El borrado lógico conserva registro y archivo; el físico borra ambos y es irreversible. Detalle completo: `doc/borrado-tickets.md`.
- **Gastos generales (R12)** — tabla `general_expenses` independiente de `tickets`: sin `creator_id`/`brand_id`, sin `budget_cycle_id`, sin `status` de validación. Se crean y cuentan de inmediato, solo `admin`/`superadmin`. Mismo patrón de soft/hard delete que tickets pero sin reversión de ciclo (no aplica). Detalle completo: `doc/gastos-generales-manual.md`.
- **Theming (`data-theme`)**: el selector en `index.css` es `[data-theme="light"]`, **sin** `:root` — a propósito, para que el reporte PDF (R8) pueda forzar tema claro en un contenedor propio (`data-theme="light"` local) sin tocar el tema real del usuario en `<html>`. No revertir a `:root[data-theme="light"]`, rompería esa plantilla off-screen.
- `jspdf` y `html2canvas` son dependencias de frontend (no dev, corren en runtime) cargadas con `import()` dinámico solo al descargar el PDF — no agregar imports estáticos de estas dos, engordarían el bundle principal.
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

Pruebas: `cd backend && python -m pytest` (167 pruebas, DB de prueba propia). E2E: archivos en `frontend/e2e/` (`auth.spec.js`, `presupuesto-flujo-completo.spec.js`, `gastos-generales.spec.js`) — correrlos por separado para no acercarse al rate limit de login (30/15min por IP); ver `doc/auth-manual-usuario.md` §Pruebas.

## Presupuestos y validación (R7/R9/R10)

Ciclos de presupuesto, estados de ticket y prioridad de marcas: reglas de negocio completas con ejemplos en `doc/presupuestos-y-validacion.md`. Resumen de las reglas que más importan está en "Reglas criticas" arriba.

## Gastos generales y borrado de tickets (R12)

Gastos operativos independientes de creadores/marcas/ciclos, y borrado lógico/físico de tickets (con reversión de ciclo si el ticket estaba aprobado): reglas de negocio completas en `doc/gastos-generales-manual.md` y `doc/borrado-tickets.md`. Resumen en "Reglas criticas" arriba.

## Deploy

No desplegado — corre local en `127.0.0.1:8000` (backend) y `127.0.0.1:5173` (frontend). Sin entorno de produccion todavia. Antes de exponer fuera de `127.0.0.1`: agregar HTTPS (obligatorio para `Secure` en cookies), CSP/HSTS, y revisar `CORS_ORIGINS` (ver RISKS.md #2 residual y `doc/auth-arquitectura.md` §6).
