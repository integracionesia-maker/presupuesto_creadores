# Contexto — Control de Presupuestos (Creadores de Contenido)

> Conexiones pool: [[CLAUDE]] | [[context_proyectos]] | [[framework_operative_enforcement/CLAUDE]] | [[framework_operative_enforcement/PLAYBOOK]] | [[framework_operative_enforcement/FRAMEWORK]]
> Recursos: [[IDENTIDAD DE MARCA/context_design]] (visual)
> Archivos del proyecto: [[CLAUDE]] | [[status]] | [[BACKLOG]] | [[RISKS]] | [[MVP_BREAKDOWN]] | [[DESIGN_SYSTEM]] | [[avances_diarios]]

## 1. Resumen

- Proyecto: Control de Presupuestos — Creadores de Contenido
- Departamento: Integraciones IA / Marketing-Influencers (Grupo Ortiz)
- Sponsor: Grupo Ortiz
- Owner: [COMPLETAR NOMBRE] (supervision: Jose Aguilar — a confirmar)
- Estado: Build activo (Fase 5)
- Fecha de inicio: no documentada — proyecto heredado, en desarrollo activo desde antes de esta entrada
- Ultima actualizacion: 2026-07-15 (fix bug React duplicado, poblado 12 meses de datos, fusion de creadores/marcas duplicados, fix KPI marcas activas)
- Clasificacion: Herramienta interna (Nivel a definir — sin auth, sin deploy, sin tests)

## 2. Problema

El equipo necesita controlar el presupuesto asignado a cada creador de contenido que colabora con las marcas de Grupo Ortiz: cuanto se le asigno, cuanto ha gastado (por ticket/comprobante) y cuanto le queda, desglosado por marca y periodo.

## 3. Objetivo

Aplicacion de control de presupuestos que:
- Registra creadores y su presupuesto inicial
- Registra tickets de gasto (monto + comprobante PNG/JPG/PDF) asociados a un creador y una marca
- Calcula gasto y restante en tiempo real por creador
- Ofrece un dashboard ejecutivo con KPIs y graficos por rango de fechas

## 4. Usuarios

- Equipo de integraciones/marketing (rol unico hoy — sin roles diferenciados, sin login)
- Sin acceso externo — uso interno local

## 5. Proceso actual

1. Se registran creadores (presupuesto inicial) y marcas via API/seed
2. Se sube un ticket (monto + archivo comprobante) asociado a creador + marca
3. El backend recalcula `spent_budget`/`remaining_budget` del creador
4. El dashboard consulta `/api/dashboard/*` filtrado por rango de fechas y muestra KPIs + 4 graficos ApexCharts

## 6. Sistema / stack

- Backend: FastAPI + SQLAlchemy + SQLite (`backend/app/`), routers `creators`, `brands`, `tickets`, `dashboard`
- Frontend: Vite 6 + React 18.3.1 + Tailwind 3, componentes en `frontend/src/components/`
- Graficos: ApexCharts via `react-apexcharts`, tema oscuro custom (`charts/apexTheme.js`)
- Sin build/deploy pipeline — corre local (`127.0.0.1:8000` / `127.0.0.1:5173`)

## 7. Entregables

Ver `MVP_BREAKDOWN.md` para detalle y evidencia.

- CRUD creadores, marcas, tickets (backend) — Hecho
- Endpoints de dashboard analytics (summary, monthly-spend, creator-usage, brand-spend) — Hecho
- Dashboard frontend: filtro de fechas + 7 KPI cards + 4 graficos ApexCharts — Hecho
- Upload de tickets con archivo adjunto — Hecho
- Datos de prueba (12 meses, sin duplicados) — Hecho
- Autenticacion / control de acceso — Pendiente
- Tests automatizados — Pendiente
- Control de versiones (git) — Pendiente
- Deploy a un entorno accesible por el equipo — Pendiente

## 8. Dependencias

- Ninguna API externa — stack 100% local (FastAPI + SQLite + Vite)
- `apexcharts` / `react-apexcharts` (graficos)
- `puppeteer` listado en un `package.json` raiz distinto (no es dependencia de este proyecto — revisar si aplica)

## 9. Riesgos

Ver `RISKS.md` para detalle completo. Top 3:
1. Sin control de versiones (no es repo git) — sin historial, sin forma de revertir cambios
2. Sin autenticacion en la API — cualquiera en la red local puede leer/modificar presupuestos
3. Sin backups de `presupuesto.db` (SQLite es un solo archivo, sin respaldo)

## 10. Metricas

- MVP: ver `MVP_BREAKDOWN.md`
- Semaforo: Verde (actividad real 2026-07-15, sin bloqueos activos)
- Tests: 0 (BACKLOG pendiente)
- Datos actuales: 6 creadores, 8 marcas, 89 tickets, 12 meses de historial (Ago 2025 - Jul 2026)

## 11. Seguridad

Ver `SECURITY.md` (pendiente de crear — no existe checklist de seguridad formal todavia). Gaps conocidos: sin auth, sin backups, sin git.

## 12. Diseno visual

- Aplica context_desing_go: Parcialmente (colores si, tipografia no)
- Fuente visual usada: `IDENTIDAD DE MARCA/context_design.md`
- Ver `DESIGN_SYSTEM.md`

## 13. Automatizacion

- Ninguna — todo el flujo (levantar servidores, seed de datos) es manual hoy

## 14. Estado actual

Backend y frontend funcionando localmente. Bug critico de React duplicado corregido (2026-07-15). Dashboard con 4 graficos ApexCharts renderizando sin errores. Datos de prueba poblados y limpios (sin duplicados de creadores/marcas). Sin git, sin auth, sin tests, sin deploy.

## 15. Siguiente paso

1. Inicializar git y hacer el primer commit (riesgo mas urgente)
2. Definir si/cuando se necesita autenticacion antes de compartir con mas gente
3. Agregar tests basicos al backend (CRUD + calculo de presupuestos)
4. Confirmar owner real del proyecto y actualizar este archivo + `status.md`
