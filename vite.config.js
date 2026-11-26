import { cloudflare } from '@cloudflare/vite-plugin'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  base: '/placeholder-path/',
  plugins: [react(), cloudflare()],
  server: {
    port: 8080,
  },
})
