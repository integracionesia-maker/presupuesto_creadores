import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  {
    to: "/",
    end: true,
    label: "Inicio",
    icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  },
  {
    to: "/dashboard",
    label: "Dashboard",
    icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zm12 0a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z",
  },
  {
    to: "/creadores",
    label: "Creadores",
    icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
  },
  {
    to: "/transacciones",
    label: "Transacciones",
    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  },
  {
    to: "/administracion",
    label: "Administración",
    icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z",
  },
];

export default function Sidebar({ collapsed, onToggle, onNewTicket }) {
  /* En <640px siempre se muestra angosto (solo íconos); el toggle aplica ≥sm */
  const widthClass = collapsed ? "w-16" : "w-16 sm:w-60";
  const labelClass = collapsed ? "hidden" : "hidden sm:inline";

  return (
    <aside
      className={`fixed left-0 top-0 z-40 flex h-full flex-col border-r transition-all duration-300 ${widthClass}`}
      style={{
        background: "var(--go-dark-800)",
        borderColor: "var(--go-dark-600)",
      }}
    >
      {/* ── Logo ──────────────────────────────────────────────────────── */}
      <div
        className="flex h-16 items-center gap-3 border-b px-3.5"
        style={{ borderColor: "var(--go-dark-600)" }}
      >
        <div
          className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-go font-display text-sm font-bold text-white"
          style={{ background: "var(--go-orange)" }}
        >
          GO
        </div>
        <div className={`${labelClass} min-w-0`}>
          <h1
            className="truncate font-display text-xs font-bold uppercase tracking-[0.08em]"
            style={{ color: "var(--go-white)" }}
          >
            Control de Presupuestos
          </h1>
          <p
            className="truncate font-body text-[10px] tracking-wide"
            style={{ color: "var(--go-gray-2)" }}
          >
            Creadores de Contenido
          </p>
        </div>
      </div>

      {/* ── Navigation ────────────────────────────────────────────────── */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-2.5 py-4">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            title={item.label}
            className="flex items-center gap-3 rounded-go px-3 py-2.5 font-display text-sm font-semibold tracking-wide transition-all duration-200"
            style={({ isActive }) => ({
              background: isActive ? "var(--go-dark-600)" : "transparent",
              color: isActive ? "var(--go-orange)" : "var(--go-gray-2)",
            })}
          >
            <svg
              className="h-5 w-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.7}
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
            </svg>
            <span className={`${labelClass} truncate`}>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* ── Nuevo Ticket ──────────────────────────────────────────────── */}
      <div className="px-2.5 pb-3">
        <button
          onClick={onNewTicket}
          title="Nuevo Ticket"
          className={`btn-go w-full ${collapsed ? "justify-center px-0" : "justify-center px-0 sm:justify-start sm:px-5"}`}
        >
          <svg className="h-4 w-4 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          <span className={labelClass}>Nuevo Ticket</span>
        </button>
      </div>

      {/* ── Collapse toggle ───────────────────────────────────────────── */}
      <button
        onClick={onToggle}
        title={collapsed ? "Expandir menú" : "Minimizar menú"}
        className="hidden items-center justify-center border-t py-3 transition-colors hover:bg-white/5 sm:flex"
        style={{ borderColor: "var(--go-dark-600)", color: "var(--go-gray-2)" }}
      >
        <svg
          className={`h-4 w-4 transition-transform duration-300 ${collapsed ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
    </aside>
  );
}
