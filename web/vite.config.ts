import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Los fixtures viven en la raíz del monorepo, fuera de web/.
  server: { fs: { allow: ['..'] } },
})
