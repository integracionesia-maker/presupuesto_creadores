import { useState, useEffect, useCallback } from "react";
import KpiCard from "./KpiCard";
import DateRangeFilter from "./DateRangeFilter";
import MonthlySpendChart from "./charts/MonthlySpendChart";
import CreatorUsageChart from "./charts/CreatorUsageChart";
import BrandSpendApexChart from "./charts/BrandSpendApexChart";
import SpendTrendChart from "./charts/SpendTrendChart";
import {
  fetchDashboardSummary,
  fetchMonthlySpend,
  fetchCreatorUsage,
  fetchBrandSpendBreakdown,
} from "../api";

function formatCurrency(amount) {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    minimumFractionDigits: 2,
  }).format(amount);
}

function fmtDateParam(d) {
  if (!d) return undefined;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export default function Dashboard({ kpi, dateRange, onDateRangeChange }) {
  const [summary, setSummary] = useState(null);
  const [monthly, setMonthly] = useState([]);
  const [creatorUsage, setCreatorUsage] = useState([]);
  const [brandSpend, setBrandSpend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const start = fmtDateParam(dateRange.start);
      const end = fmtDateParam(dateRange.end);
      const [s, m, c, b] = await Promise.all([
        fetchDashboardSummary(start, end),
        fetchMonthlySpend(start, end),
        fetchCreatorUsage(start, end),
        fetchBrandSpendBreakdown(start, end),
      ]);
      setSummary(s);
      setMonthly(m);
      setCreatorUsage(c);
      setBrandSpend(b);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const spentPct =
    kpi && kpi.total_budget > 0
      ? (kpi.total_spent / kpi.total_budget) * 100
      : 0;
  const remainingPct =
    kpi && kpi.total_budget > 0
      ? (kpi.total_remaining / kpi.total_budget) * 100
      : 0;

  return (
    <div className="space-y-8">
      {/* ── Date filter ──────────────────────────────────────────────── */}
      <DateRangeFilter
        startDate={dateRange.start}
        endDate={dateRange.end}
        onChange={onDateRangeChange}
      />

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
            Cargando dashboard...
          </span>
        </div>
      )}

      {!loading && (
        <>
          {/* ── KPI row 1: Cumulative ─────────────────────────────────── */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard
              title="Presupuesto Total"
              value={kpi ? formatCurrency(kpi.total_budget) : "—"}
              subtitle={`${kpi?.active_creators ?? 0} creadores activos`}
              accent="orange"
            />
            <KpiCard
              title="Total Gastado"
              value={kpi ? formatCurrency(kpi.total_spent) : "—"}
              subtitle={`${spentPct.toFixed(1)}% ejecutado`}
              accent="turquoise"
            />
            <KpiCard
              title="Total Disponible"
              value={kpi ? formatCurrency(kpi.total_remaining) : "—"}
              subtitle={`${remainingPct.toFixed(1)}% restante`}
              accent="sky"
            />
            <KpiCard
              title="Marcas Activas"
              value={summary?.active_brands ?? "—"}
              subtitle="con gastos en el período"
              accent="violet"
            />
          </div>

          {/* ── KPI row 2: Period-specific ────────────────────────────── */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <KpiCard
              title="Gastado en el Período"
              value={summary ? formatCurrency(summary.total_spent) : "—"}
              subtitle="según filtro de fechas"
              accent="orange"
            />
            <KpiCard
              title="Tickets"
              value={summary?.ticket_count ?? "—"}
              subtitle={`Promedio ${summary ? formatCurrency(summary.avg_ticket) : "—"} por ticket`}
              accent="turquoise"
            />
            <KpiCard
              title="Creadores Activos"
              value={creatorUsage.filter((c) => c.spent > 0).length}
              subtitle="con gastos en el período"
              accent="sky"
            />
          </div>

          {/* ── Row: Monthly bar chart ────────────────────────────────── */}
          <section className="go-card">
            <div className="flex items-center justify-between mb-6">
              <h2
                className="font-display text-sm font-bold uppercase tracking-[0.08em]"
                style={{ color: "var(--go-white)" }}
              >
                Transacciones por Mes
              </h2>
              <span className="go-eyebrow">MXN</span>
            </div>
            <MonthlySpendChart data={monthly} />
          </section>

          {/* ── Row: Brand spend + Creator usage (side by side) ────────── */}
          <div className="grid gap-8 lg:grid-cols-2">
            <section className="go-card">
              <div className="flex items-center justify-between mb-6">
                <h2
                  className="font-display text-sm font-bold uppercase tracking-[0.08em]"
                  style={{ color: "var(--go-white)" }}
                >
                  Gastos por Marca
                </h2>
                <span className="go-eyebrow">MXN</span>
              </div>
              <BrandSpendApexChart data={brandSpend} />
            </section>

            <section className="go-card">
              <div className="flex items-center justify-between mb-6">
                <h2
                  className="font-display text-sm font-bold uppercase tracking-[0.08em]"
                  style={{ color: "var(--go-white)" }}
                >
                  Uso de Presupuesto por Creador
                </h2>
                <span className="go-eyebrow">% usado</span>
              </div>
              <CreatorUsageChart data={creatorUsage} />
            </section>
          </div>

          {/* ── Row: Cumulative spend trend ────────────────────────────── */}
          <section className="go-card">
            <div className="flex items-center justify-between mb-6">
              <h2
                className="font-display text-sm font-bold uppercase tracking-[0.08em]"
                style={{ color: "var(--go-white)" }}
              >
                Tendencia de Gasto Acumulado
              </h2>
              <span className="go-eyebrow">MXN</span>
            </div>
            <SpendTrendChart data={monthly} />
          </section>
        </>
      )}
    </div>
  );
}
