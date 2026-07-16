import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function FullScreenSpinner() {
  return (
    <div
      className="flex min-h-screen items-center justify-center"
      style={{ background: "var(--go-dark-900)" }}
    >
      <div
        className="h-10 w-10 animate-spin rounded-full border-[3px]"
        style={{ borderColor: "var(--go-dark-600)", borderTopColor: "var(--go-orange)" }}
      />
    </div>
  );
}

/**
 * Guard de rutas: sin sesión -> /login (preservando destino); con sesión pero
 * must_change_password pendiente -> /perfil; con sesión pero rol no permitido -> /403.
 */
export default function ProtectedRoute({ roles, children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <FullScreenSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (user.must_change_password && location.pathname !== "/perfil") {
    return <Navigate to="/perfil" replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/403" replace />;
  }

  return children;
}
