import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development the browser talks to Vite, which proxies /api to the backend.
// In Docker/Kubernetes the same relative /api path is routed by nginx or the Ingress.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
