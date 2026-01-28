import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/user': 'http://localhost:8000',
      '/login': 'http://localhost:8000',
      '/post': 'http://localhost:8000',
      '/like': 'http://localhost:8000',
      '/unlike': 'http://localhost:8000',
    }
  }
})
