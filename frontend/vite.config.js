// Configuración de Vite con el plugin de React y proxy hacia la API.
//
// Las variables se leen del .env de la raíz del repositorio (envDir: '..').
// Solo las que empiezan por VITE_ llegan al navegador; API_BASE_URL solo se usa aquí.
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '..', '');
  const destinoApi = env.API_BASE_URL || 'http://127.0.0.1:8000';

  return {
    plugins: [react()],
    envDir: '..',
    server: {
      port: 5173,
      strictPort: true,
      // En desarrollo, /api se reenvía al backend: el navegador ve un solo origen y no depende de CORS.
      proxy: {
        '/api': { target: destinoApi, changeOrigin: true },
      },
    },
  };
});
