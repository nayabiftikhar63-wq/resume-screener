import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // Use 127.0.0.1 (not "localhost") so the proxy always uses IPv4.
        // On macOS, `localhost` resolves to ::1 first, but uvicorn with
        // --host 0.0.0.0 only binds IPv4 → connections to ::1 time out.
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
