import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // ponytail: прокси вместо VITE_API_URL — в dev и в проде путь один и тот же (/api),
    // поэтому в коде нет базового URL и нечему разъезжаться между окружениями.
    proxy: {
      '/api': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    },
  },
})
