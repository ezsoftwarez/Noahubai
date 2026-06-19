import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    proxy: {
      "/ai/ollama": {
        target: "http://127.0.0.1:11434",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/ai\/ollama/, ""),
      },
      "/noahubai": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/noahubai/, ""),
      },
      "/aihub-bridge": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/aihub-bridge/, ""),
      },
      "/win-bridge": {
        target: "http://127.0.0.1:9778",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/win-bridge/, ""),
      },
    },
  },
});
