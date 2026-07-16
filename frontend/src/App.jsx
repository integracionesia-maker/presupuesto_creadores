import { useState, useEffect, useCallback } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./components/Dashboard";
import CreatorList from "./components/CreatorList";
import TransactionTable from "./components/TransactionTable";
import UploadTicketModal from "./components/UploadTicketModal";
import AdminView from "./components/AdminView";
import { fetchCreators, fetchCreatorsKpi, fetchBrands } from "./api";

function firstOfMonth(y, m) {
  return new Date(y, m, 1);
}

function today() {
  const t = new Date();
  return new Date(t.getFullYear(), t.getMonth(), t.getDate());
}

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [modalOpen, setModalOpen] = useState(false);

  const [creators, setCreators] = useState([]);
  const [brands, setBrands] = useState([]);
  const [kpi, setKpi] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [dateRange, setDateRange] = useState(() => {
    const t = today();
    return { start: firstOfMonth(t.getFullYear(), t.getMonth()), end: t };
  });

  const loadData = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const [c, k, b] = await Promise.all([
        fetchCreators(),
        fetchCreatorsKpi(),
        fetchBrands(false), // incluye marcas inactivas para la vista de administración
      ]);
      setCreators(c);
      setKpi(k);
      setBrands(b);
    } catch (e) {
      setError(e.message);
    } finally {
      if (!silent) setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTicketCreated = () => {
    loadData();
    setModalOpen(false);
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "var(--go-dark-900)" }}>
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onNewTicket={() => setModalOpen(true)}
      />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div
            className="mb-6 rounded-go border px-4 py-3 font-body text-sm"
            style={{
              background: "rgba(229,62,62,0.08)",
              borderColor: "rgba(229,62,62,0.25)",
              color: "var(--go-error)",
            }}
          >
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-32">
            <div
              className="h-10 w-10 animate-spin rounded-full border-[3px]"
              style={{
                borderColor: "var(--go-dark-600)",
                borderTopColor: "var(--go-orange)",
              }}
            />
            <span
              className="ml-3 font-body text-sm"
              style={{ color: "var(--go-gray-2)" }}
            >
              Cargando datos...
            </span>
          </div>
        ) : (
          <>
            {activeTab === "dashboard" && (
              <Dashboard
                kpi={kpi}
                dateRange={dateRange}
                onDateRangeChange={(start, end) =>
                  setDateRange({ start, end })
                }
              />
            )}
            {activeTab === "creators" && (
              <CreatorList creators={creators} />
            )}
            {activeTab === "transactions" && (
              <TransactionTable
                creators={creators}
                brands={brands}
              />
            )}
            {activeTab === "admin" && (
              <AdminView
                creators={creators}
                brands={brands}
                onChange={() => loadData({ silent: true })}
              />
            )}
          </>
        )}
      </main>

      {modalOpen && (
        <UploadTicketModal
          creators={creators}
          brands={brands}
          onClose={() => setModalOpen(false)}
          onSuccess={handleTicketCreated}
        />
      )}
    </div>
  );
}
