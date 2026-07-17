import { useEffect, useState } from "react";
import { createUser, fetchUsers, resetUserPassword, setUserActive, updateUser } from "../api";
import { useAuth } from "../context/AuthContext";
import Modal from "./Modal";

const ROLE_LABELS = {
  superadmin: "Superadministrador",
  admin: "Administrador",
  creador: "Creador",
};

const ROLE_OPTIONS = [
  { value: "admin", label: "Administrador" },
  { value: "creador", label: "Creador" },
];

function emptyForm() {
  return { username: "", email: "", full_name: "", role: "creador", creator_id: "", password: "" };
}

export default function UserManagement({ creators }) {
  const { user: currentUser } = useAuth();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [formOpen, setFormOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState(emptyForm());
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const [confirmToggle, setConfirmToggle] = useState(null);

  const [resetResult, setResetResult] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setUsers(await fetchUsers());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreateForm = () => {
    setEditingUser(null);
    setFormData(emptyForm());
    setFormError(null);
    setFormOpen(true);
  };

  const openEditForm = (u) => {
    setEditingUser(u);
    setFormData({
      username: u.username,
      email: u.email,
      full_name: u.full_name,
      role: u.role,
      creator_id: u.creator_id || "",
      password: "",
    });
    setFormError(null);
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setEditingUser(null);
    setFormError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      const creatorId = formData.role === "creador" ? Number(formData.creator_id) || null : null;
      if (editingUser) {
        await updateUser(editingUser.id, {
          full_name: formData.full_name,
          email: formData.email,
          role: formData.role,
          creator_id: creatorId,
        });
      } else {
        await createUser({
          username: formData.username,
          email: formData.email,
          full_name: formData.full_name,
          role: formData.role,
          creator_id: creatorId,
          password: formData.password || undefined,
        });
      }
      closeForm();
      load();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleResetPassword = async (u) => {
    setError(null);
    try {
      const result = await resetUserPassword(u.id);
      setResetResult({ username: u.username, temporary_password: result.temporary_password });
    } catch (err) {
      setError(err.message);
    }
  };

  const openToggleConfirm = (u) => {
    setConfirmToggle({ user: u, newActive: !u.is_active });
  };

  const handleToggleConfirm = async () => {
    if (!confirmToggle) return;
    const { user: target, newActive } = confirmToggle;
    setSubmitting(true);
    setError(null);
    try {
      await setUserActive(target.id, newActive);
      setConfirmToggle(null);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const errorBanner = error && (
    <div
      className="rounded-go border px-4 py-3 font-body text-sm"
      style={{ background: "rgba(229,62,62,0.08)", borderColor: "rgba(229,62,62,0.25)", color: "var(--go-error)" }}
    >
      {error}
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="go-eyebrow">{users.length} usuarios</span>
        <button onClick={openCreateForm} className="btn-go">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Nuevo Usuario
        </button>
      </div>

      {errorBanner}

      {loading ? (
        <p className="font-body text-sm" style={{ color: "var(--go-text-secondary)" }}>
          Cargando...
        </p>
      ) : users.length === 0 ? (
        <div
          className="flex flex-col items-center justify-center py-16 font-body text-sm"
          style={{ color: "var(--go-text-secondary)" }}
        >
          <p>No hay usuarios registrados.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-go-lg border" style={{ borderColor: "var(--go-border)" }}>
          <table className="go-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Rol</th>
                <th className="text-center">Estado</th>
                <th className="text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => {
                const isSelf = u.id === currentUser.id;
                const isTargetSuperadmin = u.role === "superadmin";
                return (
                  <tr key={u.id}>
                    <td className="font-mono text-xs">{u.username}</td>
                    <td>
                      <span className="font-display text-sm font-semibold" style={{ color: "var(--go-text-primary)" }}>
                        {u.full_name}
                      </span>
                      {isSelf && <span className="go-badge go-badge-warning ml-2">Tú</span>}
                    </td>
                    <td className="font-body text-xs" style={{ color: "var(--go-text-secondary)" }}>
                      {u.email}
                    </td>
                    <td>
                      <span
                        className="go-badge"
                        style={{ background: "var(--go-surface-sunken)", color: "var(--go-text-secondary)" }}
                      >
                        {ROLE_LABELS[u.role] || u.role}
                      </span>
                    </td>
                    <td className="text-center">
                      <span className={`go-badge ${u.is_active ? "go-badge-success" : "go-badge-error"}`}>
                        {u.is_active ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center justify-end gap-2">
                        {!isTargetSuperadmin && (
                          <>
                            <button onClick={() => openEditForm(u)} className="btn-go-ghost text-xs px-3 py-1.5">
                              Editar
                            </button>
                            <button
                              onClick={() => handleResetPassword(u)}
                              className="btn-go-ghost text-xs px-3 py-1.5"
                            >
                              Resetear contraseña
                            </button>
                          </>
                        )}
                        {!isTargetSuperadmin && (
                          <button onClick={() => openToggleConfirm(u)} className="btn-go-ghost text-xs px-3 py-1.5">
                            {u.is_active ? "Desactivar" : "Activar"}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {formOpen && (
        <Modal title={editingUser ? "Editar Usuario" : "Crear Usuario"} onClose={closeForm} submitting={submitting}>
          <form onSubmit={handleSubmit} className="space-y-4 px-6 py-5">
            {!editingUser && (
              <div>
                <label className="go-eyebrow mb-1.5 block">Usuario</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="go-input"
                  minLength={3}
                  maxLength={50}
                  required
                />
              </div>
            )}
            <div>
              <label className="go-eyebrow mb-1.5 block">Nombre completo</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="go-input"
                maxLength={150}
                required
              />
            </div>
            <div>
              <label className="go-eyebrow mb-1.5 block">Correo</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="go-input"
                required
              />
            </div>
            <div>
              <label className="go-eyebrow mb-1.5 block">Rol</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value, creator_id: "" })}
                className="go-select"
              >
                {ROLE_OPTIONS.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>
            {formData.role === "creador" && (
              <div>
                <label className="go-eyebrow mb-1.5 block">Creador vinculado</label>
                <select
                  value={formData.creator_id}
                  onChange={(e) => setFormData({ ...formData, creator_id: e.target.value })}
                  className="go-select"
                  required
                >
                  <option value="">Selecciona un creador...</option>
                  {creators.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            {!editingUser && (
              <div>
                <label className="go-eyebrow mb-1.5 block">Contraseña (opcional)</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="go-input"
                  placeholder="Dejar en blanco para generar una temporal"
                  minLength={10}
                />
              </div>
            )}

            {formError && (
              <div
                className="rounded-go border px-4 py-3 font-body text-sm"
                style={{ background: "rgba(229,62,62,0.08)", borderColor: "rgba(229,62,62,0.25)", color: "var(--go-error)" }}
              >
                {formError}
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button type="button" onClick={closeForm} disabled={submitting} className="btn-go-ghost">
                Cancelar
              </button>
              <button type="submit" disabled={submitting} className="btn-go">
                {submitting ? "Guardando..." : editingUser ? "Guardar" : "Crear"}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {confirmToggle && (
        <Modal title="Confirmar cambio de estado" onClose={() => setConfirmToggle(null)} submitting={submitting}>
          <div className="space-y-4 px-6 py-5">
            <p className="font-body text-sm" style={{ color: "var(--go-text-primary)" }}>
              {confirmToggle.newActive
                ? `¿Reactivar a ${confirmToggle.user.full_name}?`
                : `¿Desactivar a ${confirmToggle.user.full_name}? No podrá iniciar sesión hasta que sea reactivado.`}
            </p>

            {errorBanner}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setConfirmToggle(null)}
                disabled={submitting}
                className="btn-go-ghost"
              >
                Cancelar
              </button>
              <button type="button" onClick={handleToggleConfirm} disabled={submitting} className="btn-go">
                {submitting ? "Aplicando..." : "Confirmar"}
              </button>
            </div>
          </div>
        </Modal>
      )}

      {resetResult && (
        <Modal title="Contraseña temporal generada" onClose={() => setResetResult(null)}>
          <div className="space-y-4 px-6 py-5">
            <p className="font-body text-sm" style={{ color: "var(--go-text-primary)" }}>
              Comparte esta contraseña temporal con <strong>{resetResult.username}</strong> por un canal seguro.
              Solo se muestra una vez.
            </p>
            <div className="go-input select-all font-mono">{resetResult.temporary_password}</div>
            <div className="flex justify-end">
              <button onClick={() => setResetResult(null)} className="btn-go">
                Cerrar
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
