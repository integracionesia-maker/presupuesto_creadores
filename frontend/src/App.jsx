import { useState, useEffect, useCallback } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import CreatorList from "./components/CreatorList";
import TransactionTable from "./components/TransactionTable";
import AdminView from "./components/AdminView";
import UploadTicketModal from "./components/UploadTicketModal";
import ProtectedRoute from "./components/ProtectedRoute";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import ProfilePage from "./pages/ProfilePage";
import ForbiddenPage from "./pages/ForbiddenPage";
import { useAuth } from "./context/AuthContext";
import { fetchCreators, fetchCreatorsKpi, fetchBrands } from "./api";

const ADMIN_ROLES = ["admin", "superadmin"];

function firstOfMonth(y, m) {
  return new Date(y, m, 1);
}

function today() {
  const t = new Date();
  return new Date(t.getFullYear(), t.getMonth(), t.getDate());
}

function LoadingSpinner() {
  return (
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
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function AppShell() {
  const { user } = useAuth();
  const isPrivileged = user && ADMIN_ROLES.includes(user.role);

  const [modalOpen, setModalOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(
    () => localStorage.getItem("sidebar-collapsed") === "true"
  );

  const [creators, setCreators] = useState([]);
  const [brands, setBrands] = useState([]);
  const [kpi, setKpi] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [dateRange, setDateRange] = useState(() => {
    const t = today();
    return { start: firstOfMonth(t.getFullYear(), t.getMonth()), end: t };
  });

  const handleToggleSidebar = () => {
    setSidebarCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("sidebar-collapsed", next ? "true" : "false");
      return next;
    });
  };

  const loadData = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const [c, k, b] = await Promise.all([
        fetchCreators(),
        isPrivileged ? fetchCreatorsKpi() : Promise.resolve(null),
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
  }, [isPrivileged]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTicketCreated = () => {
    loadData();
    setModalOpen(false);
  };

  return (
    <div className="min-h-screen" style={{ background: "var(--go-dark-900)" }}>
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={handleToggleSidebar}
        onNewTicket={() => setModalOpen(true)}
      />

      <main
        className={`min-h-screen transition-all duration-300 ${
          sidebarCollapsed ? "ml-16" : "ml-16 sm:ml-60"
        }`}
      >
        <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
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

          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute roles={ADMIN_ROLES}>
                  {loading ? (
                    <LoadingSpinner />
                  ) : (
                    <Dashboard
                      kpi={kpi}
                      dateRange={dateRange}
                      onDateRangeChange={(start, end) =>
                        setDateRange({ start, end })
                      }
                    />
                  )}
                </ProtectedRoute>
              }
            />
            <Route
              path="/creadores"
              element={
                <ProtectedRoute roles={ADMIN_ROLES}>
                  {loading ? <LoadingSpinner /> : <CreatorList creators={creators} />}
                </ProtectedRoute>
              }
            />
            <Route
              path="/transacciones"
              element={
                loading ? (
                  <LoadingSpinner />
                ) : (
                  <TransactionTable creators={creators} brands={brands} />
                )
              }
            />
            <Route
              path="/administracion"
              element={
                <ProtectedRoute roles={ADMIN_ROLES}>
                  {loading ? (
                    <LoadingSpinner />
                  ) : (
                    <AdminView
                      creators={creators}
                      brands={brands}
                      onChange={() => loadData({ silent: true })}
                    />
                  )}
                </ProtectedRoute>
              }
            />
            <Route path="/perfil" element={<ProfilePage />} />
            <Route path="/403" element={<ForbiddenPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
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
