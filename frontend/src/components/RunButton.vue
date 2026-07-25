<script setup lang="ts">
const props = defineProps<{
  canRun: boolean
  isRunning: boolean
  hasJustFinished: boolean
}>()

const emit = defineEmits<{
  run: []
  cancel: []
}>()

function handleClick(): void {
  if (props.isRunning) {
    emit('cancel')
  } else {
    emit('run')
  }
}
</script>

<template>
  <div class="run-bar">
    <button
      class="run-btn"
      :class="{
        running: isRunning,
        finished: hasJustFinished && !isRunning
      }"
      :disabled="!isRunning && !canRun"
      @click="handleClick"
    >
      <template v-if="isRunning">
        <span class="spinner" />
        终止
      </template>
      <template v-else-if="hasJustFinished">
        <span class="btn-icon-finish">✓</span>
        运行结束
      </template>
      <template v-else>
        <span class="btn-icon">▶</span>
        运行
      </template>
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

.run-btn.finished {
  background: var(--color-jade);
}

.run-btn.finished:hover:not(:disabled) {
  background: var(--color-jade-dark);
}

.btn-icon {
  font-size: 10px;
}

.btn-icon-finish {
  font-size: 12px;
  font-weight: 700;
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
