// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
// @ts-ignore — vitest extiende la config de vite

export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy para desarrollo local
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
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
})
/*import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})*/
