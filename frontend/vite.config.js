import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Permite apuntar a un backend en otro puerto (usado por la suite E2E de Playwright)
// sin tocar el valor por defecto de desarrollo (127.0.0.1:8000).
const backendPort = process.env.VITE_BACKEND_PORT || "8000";

export default defineConfig({
  plugins: [react()],
  resolve: {
    dedupe: ["react", "react-dom"],
  },
  optimizeDeps: {
    include: ["react", "react-dom", "react-apexcharts", "apexcharts"],
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: `http://127.0.0.1:${backendPort}`,
        changeOrigin: true,
      },
    },
  },
});
