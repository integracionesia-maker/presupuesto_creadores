# DESIGN_SYSTEM — Control de Presupuestos (Creadores de Contenido)

## Fuente visual

- Repo base: `https://github.com/joseaguilar-wq/context_desing_go.git`
- Archivo consultado: `IDENTIDAD DE MARCA/context_design.md` (no referenciado formalmente en el codigo hoy — los tokens coinciden por replicacion manual, no por vinculo real)
- Fecha de revision: 2026-07-15 (alineacion framework, primera vez que se documenta)

## Aplicacion

| Elemento | Regla aplicada | Evidencia |
|---|---|---|
| Colores | Naranja GO `#FB670B` + neutros `#262626` `#535353` `#C5C5C5` `#ECEBE0` `#FFFFFF` | `frontend/tailwind.config.js` |
| Colores de graficos | `#FB670B` `#14B8A6` `#38BDF8` `#A78BFA` `#00A36E` `#F59E0B` | `frontend/src/components/charts/apexTheme.js` |
| Tipografia | Space Grotesk (display) + Inter (body) + JetBrains Mono (mono) — **no coincide** con la tipografia oficial GO (Blauer Nue / Conthic) | `frontend/tailwind.config.js` |
| Bordes | `border-radius` 8px / 12px / 16px (`go`, `go-lg`, `go-xl`) | `frontend/tailwind.config.js` |
| Tema de graficos | Tema oscuro fijo (`goApexTheme`, `mode: "dark"`), grid y ejes con `--go-gray-2`/`--go-dark-600` | `charts/apexTheme.js` |
| Dashboard | Filtro de fechas + presets, 7 KPI cards, 4 graficos, spinner de carga, mensajes de error inline | `Dashboard.jsx` |

## Modos

Solo modo oscuro implementado (`background: var(--go-dark-900)` fijo en `App.jsx`). No hay toggle claro/oscuro como en otros proyectos del portafolio (ej. market_intelligence).

## Estados

- **Vacio:** cada grafico muestra un mensaje centrado ("Sin transacciones/datos en este periodo") cuando no hay datos
- **Error:** banda roja translucida (`rgba(229,62,62,0.08)`) con texto del mensaje de error
- **Carga:** spinner circular animado (`animate-spin`) + texto "Cargando..."
- **Exito:** KPI cards + graficos ApexCharts renderizados

## Riesgos visuales

- Tipografia no formalizada con la marca oficial (ver BACKLOG #7)
- Sin vinculo real (import/referencia) a `context_design.md` — los tokens se replicaron a mano y pueden desalinearse si la fuente cambia
- Sin modo claro — no evaluado si se requiere

## Pendientes

- Decidir si se adopta Blauer Nue / Conthic o se mantiene Space Grotesk / Inter (BACKLOG #7)
- Formalizar la fuente visual como referencia real, no solo tokens copiados

## Excepcion / decisiones

Ninguna decision de direccion registrada todavia sobre diseno visual.
