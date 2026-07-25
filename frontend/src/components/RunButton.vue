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
      <span v-if="!store.isRunning" class="btn-icon">▶</span>
      {{ store.isRunning ? '终止' : '运行' }}
    </button>
  </div>
</template>

<style scoped>
.run-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  background: #fafaf8;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.run-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 22px;
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-display);
  color: #fff;
  background: var(--color-vermillion);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.05em;
}

.run-btn:hover:not(:disabled) {
  background: var(--color-vermillion-dark);
}

.run-btn:disabled {
  background: var(--color-slate-light);
  cursor: not-allowed;
}

.run-btn.running {
  background: var(--color-ink-light);
}

.run-btn.running:hover:not(:disabled) {
  background: var(--color-ink);
}

.btn-icon {
  font-size: 10px;
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
</style>
