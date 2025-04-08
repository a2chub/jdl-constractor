/// <reference types="vitest" />
import { defineConfig } from 'vite'; // vitest/config ではなく vite からインポート
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true, // describe, it などをグローバルに利用可能にする
    environment: 'jsdom', // DOM環境をシミュレート
    setupFiles: './src/setupTests.ts', // テストセットアップファイルのパス
    // css: true, // CSSのインポートを有効にする場合 (必要に応じて)
  },
});
