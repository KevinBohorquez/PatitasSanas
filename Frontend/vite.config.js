// vite.config.js
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react-swc'
// @ts-ignore — vitest extiende la config de vite

export default defineConfig(({ mode }) => {
  // Carga las variables de entorno (.env) para el modo actual
  const env = loadEnv(mode, process.cwd(), '')
  // Destino del backend al que se reenvían las llamadas /api (ver .env.example)
  const proxyTarget = env.VITE_API_PROXY_TARGET || 'http://localhost:8000'

  return {
  plugins: [react()],
  server: {
    // Proxy para desarrollo local
    proxy: {
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path,
      }
    }
  },
  // Configuración para build de producción
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      }
    }
  },
  // Configuración de Vitest (cobertura para SonarQube)
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['lcov', 'text'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/**',
        'dist/**',
        'src/main.jsx',
        '**/*.config.*',
        '**/*.d.ts',
      ],
    },
  },
  }
})
/*import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})*/
