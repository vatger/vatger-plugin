import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { loadEnv } from "vite"
import { defineConfig } from "vite"
import path from "path"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "")

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      open: true,
      proxy: {
        "/api": {
          target: env.VITE_API_URL || "http://localhost:8000",
          ws: true,
        },
        "/static": env.VITE_API_URL || "http://localhost:8000",
      },
    },
    build: {
      outDir: "build",
      sourcemap: true,
    },
  }
})
