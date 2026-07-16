import { Link } from "react-router-dom";

const SECTIONS = [
  {
    to: "/dashboard",
    title: "Dashboard",
    description: "Resumen de gastos, KPIs y tendencias por periodo.",
    icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zm12 0a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z",
  },
  {
    to: "/creadores",
    title: "Creadores",
    description: "Consulta el presupuesto y progreso de cada creador.",
    icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
  },
  {
    to: "/transacciones",
    title: "Transacciones",
    description: "Historial detallado de tickets y comprobantes.",
    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  },
  {
    to: "/administracion",
    title: "Administración",
    description: "Gestiona creadores, marcas y estados del sistema.",
    icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-10">
      {/* ── Welcome ───────────────────────────────────────────────────── */}
      <div className="mx-auto max-w-2xl pt-8 text-center">
        <p className="go-eyebrow mb-3">Grupo Ortiz</p>
        <h1
          className="font-display text-2xl font-bold uppercase tracking-[0.04em] sm:text-3xl"
          style={{ color: "var(--go-white)" }}
        >
          Bienvenido al Control de Presupuestos
        </h1>
        <p
          className="mt-3 font-body text-sm sm:text-base"
          style={{ color: "var(--go-gray-2)" }}
        >
          Gestiona los presupuestos de creadores de contenido, registra
          tickets de gasto y monitorea el desempeño de cada campaña.
        </p>
      </div>

      {/* ── Section cards ─────────────────────────────────────────────── */}
      <div className="mx-auto grid max-w-4xl grid-cols-1 gap-6 sm:grid-cols-2">
        {SECTIONS.map((s) => (
          <Link
            key={s.to}
            to={s.to}
            className="go-card group transition-all duration-200 hover:-translate-y-0.5"
            style={{ textDecoration: "none" }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--go-orange)")}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--go-dark-600)")}
          >
            <div
              className="flex h-12 w-12 items-center justify-center rounded-go-lg transition-colors duration-200 group-hover:bg-[var(--go-orange-tint)]"
              style={{ background: "var(--go-dark-600)" }}
            >
              <svg
                className="h-6 w-6 transition-colors duration-200 group-hover:text-[var(--go-orange)]"
                style={{ color: "var(--go-gray-2)" }}
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d={s.icon} />
              </svg>
            </div>
            <h3
              className="mt-4 font-display text-base font-bold uppercase tracking-[0.06em]"
              style={{ color: "var(--go-white)" }}
            >
              {s.title}
            </h3>
            <p
              className="mt-1.5 font-body text-sm"
              style={{ color: "var(--go-gray-2)" }}
            >
              {s.description}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
