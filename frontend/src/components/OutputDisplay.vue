<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  lines: string[]
}>()

const scrollContainer = ref<HTMLElement | null>(null)

watch(
  () => props.lines.length,
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  },
)
</script>

<template>
  <div class="output-display">
    <div class="output-header">
      <span class="header-icon">◇</span>
      <span>输出</span>
    </div>
    <div ref="scrollContainer" class="output-body">
      <template v-if="lines.length > 0">
        <div
          v-for="(line, i) in lines"
          :key="i"
          class="output-line"
        >
          {{ line }}
        </div>
      </template>
      <div v-else class="output-placeholder">
        程序输出将显示于此…
      </div>
    </div>
  </div>
</template>

<style scoped>
.output-display {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.output-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-slate);
  background: #fafaf8;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
  font-family: var(--font-display);
}

.header-icon {
  color: var(--color-gold);
  font-size: 10px;
}

.output-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  background: #fdfcf7;
  font-family: var(--font-display);
  font-size: 17px;
  line-height: 2;
  color: var(--color-ink);
}

.output-line {
  padding: 1px 0;
}

.output-line::before {
  content: '》';
  color: var(--color-slate-light);
  margin-right: 6px;
  font-size: 14px;
}

.output-placeholder {
  color: #d1cbc0;
  font-style: italic;
}
</style>
