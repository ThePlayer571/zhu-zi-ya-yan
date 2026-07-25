<script setup lang="ts">
import { ref, computed } from 'vue'
import { useProgramStore } from '../stores/program'
import type { TraceEntry } from '../types'

const store = useProgramStore()
const isExpanded = ref(false)

const hasEntries = computed(() => store.traceEntries.length > 0)

function toggle(): void {
  isExpanded.value = !isExpanded.value
}

/** 格式化单条记录，返回经注疏文本行数组。 */
function formatEntry(entry: TraceEntry): string[] {
  const lines: string[] = []

  // 函数进入/退出使用简单格式
  if (entry.statement_name === '起章') {
    lines.push(`起${entry.details['函数名'] ?? ''}`)
    return lines
  }
  if (entry.statement_name === '毕章') {
    lines.push(`毕${entry.details['函数名'] ?? ''}`)
    return lines
  }

  // 经注疏格式
  if (entry.source_code) {
    lines.push(`【经】${entry.source_code}`)
  }
  lines.push(`【注】${entry.statement_description}`)
  if (entry.change) {
    lines.push(`【疏】${entry.change}`)
  }

  // 注解
  for (const [key, content] of Object.entries(entry.annotations)) {
    lines.push(`【${key}】${content}`)
  }

  return lines
}
</script>

<template>
  <div class="trace-panel">
    <button class="trace-toggle" @click="toggle">
      查看复盘
      <span class="toggle-icon">{{ isExpanded ? '▾' : '▸' }}</span>
      <span
        v-if="hasEntries && !isExpanded"
        class="entry-count"
      >
        ({{ store.traceEntries.length }})
      </span>
    </button>

    <div v-if="isExpanded" class="trace-body">
      <template v-if="hasEntries">
        <div
          v-for="(entry, i) in store.traceEntries"
          :key="i"
          class="trace-entry"
        >
          <template v-for="(line, j) in formatEntry(entry)" :key="j">
            <div
              class="trace-line"
              :class="{
                'trace-jing': line.startsWith('【经】'),
                'trace-zhu': line.startsWith('【注】'),
                'trace-shu': line.startsWith('【疏】'),
                'trace-func': line.startsWith('起') || line.startsWith('毕'),
                'trace-annotation': line.startsWith('【') && !line.startsWith('【经】') && !line.startsWith('【注】') && !line.startsWith('【疏】'),
              }"
            >
              {{ line }}
            </div>
          </template>
          <div
            v-if="i < store.traceEntries.length - 1"
            class="trace-separator"
          />
        </div>
      </template>
      <div v-else class="trace-empty">
        无执行记录
      </div>
    </div>
  </div>
</template>

<style scoped>
.trace-panel {
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.trace-toggle {
  width: 100%;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  background: #f9fafb;
  border: none;
  border-bottom: 1px solid #e5e7eb;
  cursor: pointer;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 6px;
}

.trace-toggle:hover {
  background: #f3f4f6;
}

.toggle-icon {
  font-size: 10px;
}

.entry-count {
  font-weight: 400;
  color: #9ca3af;
}

.trace-body {
  max-height: 300px;
  overflow-y: auto;
  padding: 10px 12px;
  background: #fafafa;
  font-family: 'Noto Serif SC', 'Source Han Serif SC', 'SimSun', serif;
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
}

.trace-entry {
  margin-bottom: 4px;
}

.trace-line {
  padding: 1px 0;
}

.trace-func {
  font-weight: 700;
  font-size: 15px;
  color: #1f2937;
  padding: 4px 0;
}

.trace-jing {
  font-weight: 600;
  color: #1f2937;
}

.trace-zhu {
  color: #4b5563;
  padding-left: 8px;
}

.trace-shu {
  color: #6b7280;
  padding-left: 8px;
  font-size: 13px;
}

.trace-annotation {
  color: #9ca3af;
  padding-left: 4px;
  font-size: 12px;
}

.trace-separator {
  height: 1px;
  background: #e5e7eb;
  margin: 6px 0;
}

.trace-empty {
  color: #d1d5db;
  font-style: italic;
  text-align: center;
  padding: 16px 0;
}
</style>
