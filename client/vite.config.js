import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  },
  preview: {
    port: 10001,
    strictPort: false,
    host: '0.0.0.0',
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'cv-tailor-frontend-9gun.onrender.com',
      '*.onrender.com',
      '*.railway.app',
      '*.herokuapp.com',
      '*.digitalocean.app'
    ]
  }
})
