import { useState, useEffect } from "react";
import { fetchTickets, ticketFileUrl } from "../api";

function formatCurrency(amount) {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    minimumFractionDigits: 2,
  }).format(amount);
}

function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("es-MX", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function TransactionTable({ creators, brands }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [filterCreator, setFilterCreator] = useState("");
  const [filterBrand, setFilterBrand] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchTickets({
      creatorName: filterCreator || undefined,
      brandName: filterBrand || undefined,
    })
      .then((data) => {
        if (!cancelled) setTickets(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [filterCreator, filterBrand]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2
          className="font-display text-lg font-bold uppercase tracking-[0.06em]"
          style={{ color: "var(--go-white)" }}
        >
          Historial de Transacciones
        </h2>
        <span className="go-eyebrow">
          {tickets.length} registros
        </span>
      </div>

      {/* ── Filters ──────────────────────────────────────────────────── */}
      <div
        className="flex flex-wrap gap-4 rounded-go-lg p-4"
        style={{ background: "var(--go-dark-800)", border: "1px solid var(--go-dark-600)" }}
      >
        <div className="min-w-[200px] flex-1">
          <label className="go-eyebrow mb-1.5 block">Filtrar por Creador</label>
          <div className="relative">
            <input
              type="text"
              value={filterCreator}
              onChange={(e) => setFilterCreator(e.target.value)}
              placeholder="Nombre del creador..."
              className="go-input pl-9"
            />
            <svg
              className="absolute left-3 top-[11px] h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
              style={{ color: "var(--go-gray-1)" }}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
        </div>

        <div className="min-w-[200px] flex-1">
          <label className="go-eyebrow mb-1.5 block">Filtrar por Marca</label>
          <select
            value={filterBrand}
            onChange={(e) => setFilterBrand(e.target.value)}
            className="go-select"
          >
            <option value="">Todas las marcas</option>
            {brands.map((b) => (
              <option key={b.id} value={b.name}>
                {b.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* ── Error ─────────────────────────────────────────────────────── */}
      {error && (
        <div
          className="rounded-go border px-4 py-3 font-body text-sm"
          style={{
            background: "rgba(229,62,62,0.08)",
            borderColor: "rgba(229,62,62,0.25)",
            color: "var(--go-error)",
          }}
        >
          {error}
        </div>
      )}

      {/* ── Loading ───────────────────────────────────────────────────── */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <div
            className="h-8 w-8 animate-spin rounded-full border-[3px]"
            style={{
              borderColor: "var(--go-dark-600)",
              borderTopColor: "var(--go-orange)",
            }}
          />
          <span
            className="ml-3 font-body text-sm"
            style={{ color: "var(--go-gray-2)" }}
          >
            Cargando transacciones...
          </span>
        </div>
      )}

      {/* ── Empty state ───────────────────────────────────────────────── */}
      {!loading && tickets.length === 0 && (
        <div
          className="flex flex-col items-center justify-center py-16 font-body text-sm"
          style={{ color: "var(--go-gray-2)" }}
        >
          <svg
            className="mb-3 h-10 w-10"
            fill="none"
            stroke="currentColor"
            strokeWidth={1}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p>No hay transacciones registradas.</p>
        </div>
      )}

      {/* ── Table ─────────────────────────────────────────────────────── */}
      {!loading && tickets.length > 0 && (
        <div
          className="overflow-x-auto rounded-go-lg border"
          style={{ borderColor: "var(--go-dark-600)" }}
        >
          <table className="go-table">
            <thead>
              <tr>
                <th>Fecha de carga</th>
                <th>Creador</th>
                <th>Marca</th>
                <th className="text-right">Monto</th>
                <th className="text-center">Comprobante</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((t) => (
                <tr key={t.id}>
                  <td style={{ color: "var(--go-gray-2)" }}>
                    {formatDate(t.upload_date)}
                  </td>
                  <td>
                    <span
                      className="font-display text-sm font-semibold"
                      style={{ color: "var(--go-white)" }}
                    >
                      {t.creator_name || `ID ${t.creator_id}`}
                    </span>
                  </td>
                  <td style={{ color: "#d4d4d4" }}>
                    {t.brand_name || `ID ${t.brand_id}`}
                  </td>
                  <td className="num text-right font-semibold" style={{ color: "var(--go-warning)" }}>
                    {formatCurrency(t.amount)}
                  </td>
                  <td className="text-center">
                    <a
                      href={ticketFileUrl(t.id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-go-ghost text-xs px-3 py-1.5"
                    >
                      <svg
                        className="h-3.5 w-3.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                      </svg>
                      Ver
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
