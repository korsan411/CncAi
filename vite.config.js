// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: ".",          // خلي الجذر هو نفس مكان index.html
  build: {
    outDir: "dist"
  }
})
