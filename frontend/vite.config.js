import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 开发模式下将 API 请求代理到 FastAPI 后端
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/chat': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/upload': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/datasets': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/switch': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/data': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/current': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/health': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/info': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/settings': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})