

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// this means frontend call - http://localhost:5173/api/auth/login
// vite forwards it to  -  http://localhost:8000/api/auth/login
// https://vite.dev/config/ 

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
