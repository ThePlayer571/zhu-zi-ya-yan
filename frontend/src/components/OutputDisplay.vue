<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useProgramStore } from '../stores/program'

const store = useProgramStore()
const scrollContainer = ref<HTMLElement | null>(null)

/** 当有新输出时自动滚到底部。 */
watch(
  () => store.output.length,
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
    <div class="output-header">输出</div>
    <div ref="scrollContainer" class="output-body">
      <template v-if="store.output.length > 0">
        <div
          v-for="(line, i) in store.output"
          :key="i"
          class="output-line"
        >
          {{ line }}
        </div>
      </template>
      <div v-else class="output-placeholder">
        程序输出将显示于此...
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
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.output-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: #fffbeb;
  font-family: 'Noto Serif SC', 'Source Han Serif SC', 'SimSun', serif;
  font-size: 16px;
  line-height: 1.8;
  color: #1f2937;
}

.output-line {
  padding: 2px 0;
}

.output-line::before {
  content: '》 ';
  color: #9ca3af;
}

.output-placeholder {
  color: #d1d5db;
  font-style: italic;
}
</style>
