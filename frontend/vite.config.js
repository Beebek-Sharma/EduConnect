import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const railwayPublicDomain =
  process.env.RAILWAY_PUBLIC_DOMAIN || 'educonnect-app-production.up.railway.app';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        credentials: 'include', // Important for cookies
        // Don't rewrite the path - keep /api prefix
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  preview: {
    host: '0.0.0.0',
    allowedHosts: [railwayPublicDomain]
  },
  build: {
    // Configure how assets are built
    rollupOptions: {
      output: {
        // Configure the crossOrigin attribute for assets
        // This sets attributes for generated assets
        generatedCode: {
          preset: 'es2015',
          symbols: false
        }
      }
    }
  }
});