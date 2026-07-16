import { defineConfig } from "@playwright/test";

// La suite E2E asume que backend y frontend YA están corriendo (ver
// doc/auth-manual-usuario.md / README de pruebas) — no orquesta los
// servidores por sí misma para evitar depender del ciclo de vida de
// `webServer` de Playwright junto a un backend Python con estado en SQLite.
const FRONTEND_URL = process.env.E2E_BASE_URL || "http://127.0.0.1:5175";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: FRONTEND_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
});
