export default function Navbar({ activeTab, onTabChange, onNewTicket }) {
  const tabs = [
    { key: "dashboard", label: "Dashboard" },
    { key: "creators", label: "Creadores" },
    { key: "transactions", label: "Transacciones" },
  ];

  return (
    <header
      className="sticky top-0 z-30 border-b"
      style={{
        background: "var(--go-dark-800)",
        borderColor: "var(--go-dark-600)",
      }}
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* ── Logo / brand ──────────────────────────────────────────── */}
        <div className="flex items-center gap-3">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-go font-display text-sm font-bold text-white"
            style={{ background: "var(--go-orange)" }}
          >
            GO
          </div>
          <div className="hidden sm:block">
            <h1
              className="font-display text-sm font-bold uppercase tracking-[0.08em]"
              style={{ color: "var(--go-white)" }}
            >
              Control de Presupuestos
            </h1>
            <p
              className="font-body text-[11px] tracking-wide"
              style={{ color: "var(--go-gray-2)" }}
            >
              Creadores de Contenido
            </p>
          </div>
        </div>

        {/* ── Tabs ──────────────────────────────────────────────────── */}
        <nav
          className="hidden sm:flex items-center gap-1 rounded-go p-1"
          style={{ background: "var(--go-dark-900)" }}
        >
          {tabs.map((t) => {
            const isActive = activeTab === t.key;
            return (
              <button
                key={t.key}
                onClick={() => onTabChange(t.key)}
                className="rounded-go px-4 py-1.5 font-display text-sm font-semibold tracking-wide transition-all duration-200"
                style={{
                  background: isActive ? "var(--go-dark-600)" : "transparent",
                  color: isActive ? "var(--go-orange)" : "var(--go-gray-2)",
                }}
              >
                {t.label}
              </button>
            );
          })}
        </nav>

        {/* ── Mobile tab selector ───────────────────────────────────── */}
        <select
          className="go-select sm:hidden w-auto"
          value={activeTab}
          onChange={(e) => onTabChange(e.target.value)}
        >
          {tabs.map((t) => (
            <option key={t.key} value={t.key}>
              {t.label}
            </option>
          ))}
        </select>

        {/* ── New ticket CTA ────────────────────────────────────────── */}
        <button onClick={onNewTicket} className="btn-go">
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span className="hidden sm:inline">Nuevo Ticket</span>
        </button>
      </div>
    </header>
  );
}
