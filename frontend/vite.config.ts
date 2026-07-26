import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  define: {
    // Vercel 构建时 VERCEL=1，注入为编译时常量供 stores 做环境判断
    // 本地构建时为 false，WebSocket 代码路径保持不变
    __VERCEL__: process.env.VERCEL ? 'true' : 'false',
  },
  server: {
    proxy: {
      // 将 /api REST 请求转发到后端
      '/api': 'http://localhost:8000',
      // 将 /ws WebSocket 请求转发到后端
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
