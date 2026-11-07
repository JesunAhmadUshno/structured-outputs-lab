import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// The site reads the repo's level-*/ results, cases, corpus and tests at build time, so every number is generated, never typed.
export default defineConfig({
  base: '/structured-outputs-lab/',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
});
