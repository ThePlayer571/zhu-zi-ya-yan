<script setup lang="ts">
import { useProgramStore } from '../stores/program'

const store = useProgramStore()

function handleClick(): void {
  if (store.isRunning) {
    store.cancelProgram()
  } else {
    store.runProgram()
  }
}
</script>

<template>
  <div class="run-bar">
    <button
      class="run-btn"
      :class="{ running: store.isRunning }"
      :disabled="!store.isRunning && !store.canRun"
      @click="handleClick"
    >
      <span v-if="store.isRunning" class="spinner" />
      {{ store.isRunning ? '取消' : '运行' }}
    </button>
    <span class="status-text">
      <span
        class="status-dot"
        :class="store.connectionStatus"
      />
      {{ store.connectionStatus === 'connected' ? '已连接' : '未连接' }}
    </span>
  </div>
</template>

<style scoped>
.run-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.run-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  background: #1d4ed8;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.run-btn:hover:not(:disabled) {
  background: #1e40af;
}

.run-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.run-btn.running {
  background: #dc2626;
}

.run-btn.running:hover:not(:disabled) {
  background: #b91c1c;
}

.spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-text {
  font-size: 12px;
  color: #6b7280;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d1d5db;
}

.status-dot.connected {
  background: #22c55e;
}

.status-dot.error {
  background: #ef4444;
}

.status-dot.connecting {
  background: #f59e0b;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
