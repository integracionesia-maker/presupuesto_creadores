import { useState } from "react";
import { createCreator, updateCreator, createBrand, updateBrand } from "../api";
import Modal from "./Modal";
import UserManagement from "./UserManagement";

function formatCurrency(amount) {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    minimumFractionDigits: 2,
  }).format(amount);
}

const SECTIONS = [
  { key: "creators", label: "Creadores" },
  { key: "brands", label: "Marcas" },
  { key: "users", label: "Usuarios" },
];

export default function AdminView({ creators, brands, onChange }) {
  const [section, setSection] = useState("creators");

  /* Creator form modal (create when editingCreator === null, edit otherwise) */
  const [creatorFormOpen, setCreatorFormOpen] = useState(false);
  const [editingCreator, setEditingCreator] = useState(null);

  /* Brand form modal */
  const [brandFormOpen, setBrandFormOpen] = useState(false);
  const [editingBrand, setEditingBrand] = useState(null);

  /* Activation toggle confirmation: { type: "creator"|"brand", item, newActive } */
  const [confirmToggle, setConfirmToggle] = useState(null);

  /* Shared form state (only one modal is open at a time) */
  const [formName, setFormName] = useState("");
  const [formBudget, setFormBudget] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  /* ── Open / close helpers ────────────────────────────────────────────── */

  const resetFeedback = () => {
    setError(null);
    setSuccessMsg(null);
  };

  const openCreatorForm = (creator = null) => {
    resetFeedback();
    setEditingCreator(creator);
    setFormName(creator ? creator.name : "");
    setFormBudget(creator ? String(creator.initial_budget) : "");
    setCreatorFormOpen(true);
  };

  const closeCreatorForm = () => {
    setCreatorFormOpen(false);
    setEditingCreator(null);
    resetFeedback();
  };

  const openBrandForm = (brand = null) => {
    resetFeedback();
    setEditingBrand(brand);
    setFormName(brand ? brand.name : "");
    setBrandFormOpen(true);
  };

  const closeBrandForm = () => {
    setBrandFormOpen(false);
    setEditingBrand(null);
    resetFeedback();
  };

  const openConfirmToggle = (type, item) => {
    resetFeedback();
    setConfirmToggle({ type, item, newActive: !item.is_active });
  };

  const closeConfirmToggle = () => {
    setConfirmToggle(null);
    resetFeedback();
  };

  /* ── Submit handlers ─────────────────────────────────────────────────── */

  const handleCreatorSubmit = async (e) => {
    e.preventDefault();
    resetFeedback();

    const name = formName.trim();
    if (!name) {
      setError("El nombre es obligatorio.");
      return;
    }
    if (name.length > 100) {
      setError("El nombre no puede exceder 100 caracteres.");
      return;
    }
    if (!formBudget || Number(formBudget) <= 0) {
      setError("El presupuesto inicial debe ser mayor a $0.");
      return;
    }

    setSubmitting(true);
    try {
      const payload = { name, initial_budget: Number(formBudget) };
      if (editingCreator) {
        await updateCreator(editingCreator.id, payload);
      } else {
        await createCreator(payload);
      }
      setSuccessMsg("Creador guardado exitosamente.");
      setTimeout(() => {
        closeCreatorForm();
        onChange();
      }, 800);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleBrandSubmit = async (e) => {
    e.preventDefault();
    resetFeedback();

    const name = formName.trim();
    if (!name) {
      setError("El nombre es obligatorio.");
      return;
    }
    if (name.length > 100) {
      setError("El nombre no puede exceder 100 caracteres.");
      return;
    }

    setSubmitting(true);
    try {
      if (editingBrand) {
        await updateBrand(editingBrand.id, { name });
      } else {
        await createBrand({ name });
      }
      setSuccessMsg("Marca guardada exitosamente.");
      setTimeout(() => {
        closeBrandForm();
        onChange();
      }, 800);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleConfirm = async () => {
    if (!confirmToggle) return;
    resetFeedback();
    setSubmitting(true);
    try {
      const { type, item, newActive } = confirmToggle;
      if (type === "creator") {
        await updateCreator(item.id, { is_active: newActive });
      } else {
        await updateBrand(item.id, { is_active: newActive });
      }
      setConfirmToggle(null);
      onChange();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  /* ── Derived ─────────────────────────────────────────────────────────── */

  const budgetWarning =
    editingCreator &&
    formBudget !== "" &&
    Number(formBudget) < editingCreator.spent_budget;

  const toggleText = confirmToggle
    ? confirmToggle.type === "creator"
      ? confirmToggle.newActive
        ? `¿Reactivar al creador ${confirmToggle.item.name}?`
        : `Al desactivar a ${confirmToggle.item.name}, no podrá recibir tickets nuevos hasta que sea reactivado.`
      : confirmToggle.newActive
      ? `¿Reactivar la marca ${confirmToggle.item.name}?`
      : `¿Desactivar la marca ${confirmToggle.item.name}? Las marcas inactivas no aparecerán en el registro de tickets.`
    : "";

  /* ── Shared banner styles ────────────────────────────────────────────── */

  const errorBanner = error && (
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
  );

  const successBanner = successMsg && (
    <div
      className="rounded-go border px-4 py-3 font-body text-sm"
      style={{
        background: "rgba(0,163,110,0.08)",
        borderColor: "rgba(0,163,110,0.25)",
        color: "var(--go-success)",
      }}
    >
      {successMsg}
    </div>
  );

  /* ── Render ──────────────────────────────────────────────────────────── */

  return (
    <div className="space-y-6">
      {/* ── Header + section tabs ──────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2
          className="font-display text-lg font-bold uppercase tracking-[0.06em]"
          style={{ color: "var(--go-white)" }}
        >
          Administración
        </h2>
        <nav
          className="flex items-center gap-1 rounded-go p-1"
          style={{ background: "var(--go-dark-800)" }}
        >
          {SECTIONS.map((s) => {
            const isActive = section === s.key;
            return (
              <button
                key={s.key}
                onClick={() => setSection(s.key)}
                className="rounded-go px-4 py-1.5 font-display text-sm font-semibold tracking-wide transition-all duration-200"
                style={{
                  background: isActive ? "var(--go-dark-600)" : "transparent",
                  color: isActive ? "var(--go-orange)" : "var(--go-gray-2)",
                }}
              >
                {s.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* ── Creators section ───────────────────────────────────────────── */}
      {section === "creators" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="go-eyebrow">{creators.length} creadores</span>
            <button onClick={() => openCreatorForm()} className="btn-go">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              Nuevo Creador
            </button>
          </div>

          {creators.length === 0 ? (
            <div
              className="flex flex-col items-center justify-center py-16 font-body text-sm"
              style={{ color: "var(--go-gray-2)" }}
            >
              <svg className="mb-3 h-10 w-10" fill="none" stroke="currentColor" strokeWidth={1} viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <p>No hay creadores registrados.</p>
            </div>
          ) : (
            <div
              className="overflow-x-auto rounded-go-lg border"
              style={{ borderColor: "var(--go-dark-600)" }}
            >
              <table className="go-table">
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th className="text-right">Presupuesto</th>
                    <th className="text-right">Gastado</th>
                    <th className="text-right">Restante</th>
                    <th className="text-center">Estado</th>
                    <th className="text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {creators.map((c) => (
                    <tr key={c.id}>
                      <td>
                        <span
                          className="font-display text-sm font-semibold"
                          style={{ color: "var(--go-white)" }}
                        >
                          {c.name}
                        </span>
                      </td>
                      <td className="num text-right">{formatCurrency(c.initial_budget)}</td>
                      <td className="num text-right" style={{ color: "var(--go-warning)" }}>
                        {formatCurrency(c.spent_budget)}
                      </td>
                      <td
                        className="num text-right font-semibold"
                        style={{
                          color: c.remaining_budget <= 0 ? "var(--go-error)" : "var(--go-success)",
                        }}
                      >
                        {formatCurrency(c.remaining_budget)}
                      </td>
                      <td className="text-center">
                        <span className={`go-badge ${c.is_active ? "go-badge-success" : "go-badge-error"}`}>
                          {c.is_active ? "Activo" : "Inactivo"}
                        </span>
                      </td>
                      <td>
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openCreatorForm(c)}
                            className="btn-go-ghost text-xs px-3 py-1.5"
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => openConfirmToggle("creator", c)}
                            className="btn-go-ghost text-xs px-3 py-1.5"
                          >
                            {c.is_active ? "Desactivar" : "Activar"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Brands section ─────────────────────────────────────────────── */}
      {section === "brands" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="go-eyebrow">{brands.length} marcas</span>
            <button onClick={() => openBrandForm()} className="btn-go">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              Nueva Marca
            </button>
          </div>

          {brands.length === 0 ? (
            <div
              className="flex flex-col items-center justify-center py-16 font-body text-sm"
              style={{ color: "var(--go-gray-2)" }}
            >
              <svg className="mb-3 h-10 w-10" fill="none" stroke="currentColor" strokeWidth={1} viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M7 7h.01M7 3h5a2 2 0 011.414.586l7 7a2 2 0 010 2.828l-5 5a2 2 0 01-2.828 0l-7-7A2 2 0 015 8V5a2 2 0 012-2z"
                />
              </svg>
              <p>No hay marcas registradas.</p>
            </div>
          ) : (
            <div
              className="overflow-x-auto rounded-go-lg border"
              style={{ borderColor: "var(--go-dark-600)" }}
            >
              <table className="go-table">
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th className="text-center">Estado</th>
                    <th className="text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {brands.map((b) => (
                    <tr key={b.id}>
                      <td>
                        <span
                          className="font-display text-sm font-semibold"
                          style={{ color: "var(--go-white)" }}
                        >
                          {b.name}
                        </span>
                      </td>
                      <td className="text-center">
                        <span className={`go-badge ${b.is_active ? "go-badge-success" : "go-badge-error"}`}>
                          {b.is_active ? "Activa" : "Inactiva"}
                        </span>
                      </td>
                      <td>
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openBrandForm(b)}
                            className="btn-go-ghost text-xs px-3 py-1.5"
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => openConfirmToggle("brand", b)}
                            className="btn-go-ghost text-xs px-3 py-1.5"
                          >
                            {b.is_active ? "Desactivar" : "Activar"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Users section ──────────────────────────────────────────────── */}
      {section === "users" && <UserManagement creators={creators} />}

      {/* ── Creator create/edit modal ──────────────────────────────────── */}
      {creatorFormOpen && (
        <Modal
          title={editingCreator ? "Editar Creador" : "Crear Creador"}
          onClose={closeCreatorForm}
          submitting={submitting}
        >
          <form onSubmit={handleCreatorSubmit} className="space-y-4 px-6 py-5">
            <div>
              <label className="go-eyebrow mb-1.5 block">Nombre</label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Nombre del creador..."
                className="go-input"
                maxLength={100}
                required
              />
            </div>

            <div>
              <label className="go-eyebrow mb-1.5 block">Presupuesto Inicial</label>
              <div className="relative">
                <span
                  className="absolute left-3.5 top-[10px] font-mono text-sm"
                  style={{ color: "var(--go-gray-2)" }}
                >
                  $
                </span>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={formBudget}
                  onChange={(e) => setFormBudget(e.target.value)}
                  placeholder="0.00"
                  className="go-input pl-7 font-mono"
                  required
                />
              </div>
            </div>

            {budgetWarning && (
              <div
                className="rounded-go border px-4 py-3 font-body text-sm"
                style={{
                  background: "rgba(245,158,11,0.08)",
                  borderColor: "rgba(245,158,11,0.25)",
                  color: "var(--go-warning)",
                }}
              >
                Atención: el nuevo presupuesto ({formatCurrency(Number(formBudget))}) es
                menor al gasto actual ({formatCurrency(editingCreator.spent_budget)}). El
                presupuesto restante quedará negativo.
              </div>
            )}

            {errorBanner}
            {successBanner}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={closeCreatorForm}
                disabled={submitting}
                className="btn-go-ghost"
              >
                Cancelar
              </button>
              <button type="submit" disabled={submitting} className="btn-go">
                {submitting ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Guardando...
                  </>
                ) : editingCreator ? (
                  "Guardar"
                ) : (
                  "Crear"
                )}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* ── Brand create/edit modal ────────────────────────────────────── */}
      {brandFormOpen && (
        <Modal
          title={editingBrand ? "Editar Marca" : "Crear Marca"}
          onClose={closeBrandForm}
          submitting={submitting}
        >
          <form onSubmit={handleBrandSubmit} className="space-y-4 px-6 py-5">
            <div>
              <label className="go-eyebrow mb-1.5 block">Nombre</label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Nombre de la marca..."
                className="go-input"
                maxLength={100}
                required
              />
            </div>

            {errorBanner}
            {successBanner}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={closeBrandForm}
                disabled={submitting}
                className="btn-go-ghost"
              >
                Cancelar
              </button>
              <button type="submit" disabled={submitting} className="btn-go">
                {submitting ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Guardando...
                  </>
                ) : editingBrand ? (
                  "Guardar"
                ) : (
                  "Crear"
                )}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* ── Toggle confirmation modal ──────────────────────────────────── */}
      {confirmToggle && (
        <Modal
          title="Confirmar cambio de estado"
          onClose={closeConfirmToggle}
          submitting={submitting}
        >
          <div className="space-y-4 px-6 py-5">
            <p className="font-body text-sm" style={{ color: "#d4d4d4" }}>
              {toggleText}
            </p>

            {errorBanner}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={closeConfirmToggle}
                disabled={submitting}
                className="btn-go-ghost"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleToggleConfirm}
                disabled={submitting}
                className="btn-go"
              >
                {submitting ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Aplicando...
                  </>
                ) : (
                  "Confirmar"
                )}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
