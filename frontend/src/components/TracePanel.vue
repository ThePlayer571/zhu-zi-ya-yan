<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TraceEntry } from '../types'

const props = withDefaults(defineProps<{
  entries: TraceEntry[]
  alwaysOpen?: boolean
}>(), {
  alwaysOpen: false,
})

const isExpanded = ref(false)

const hasEntries = computed(() => props.entries.length > 0)

function toggle(): void {
  if (props.alwaysOpen) return
  isExpanded.value = !isExpanded.value
}

/** 是否显示正文内容 */
const showBody = computed(() => props.alwaysOpen || isExpanded.value)

function formatEntry(entry: TraceEntry): string[] {
  const lines: string[] = []

  if (entry.statement_name === '起章') {
    lines.push(`起${entry.details['函数名'] ?? ''}`)
    return lines
  }
  if (entry.statement_name === '毕章') {
    lines.push(`毕${entry.details['函数名'] ?? ''}`)
    return lines
  }

  if (entry.source_code) {
    lines.push(`【经】${entry.source_code}`)
  }
  lines.push(`【注】${entry.statement_description}`)
  if (entry.change) {
    lines.push(`【疏】${entry.change}`)
  }

  for (const [key, content] of Object.entries(entry.annotations)) {
    lines.push(`【${key}】${content}`)
  }

  return lines
}
</script>

<template>
  <div class="trace-panel" :class="{ 'full-height': alwaysOpen }">
    <!-- 仅在非 alwaysOpen 模式下显示折叠按钮 -->
    <button
      v-if="!alwaysOpen"
      class="trace-toggle"
      @click="toggle"
    >
      <span class="toggle-label">经注疏</span>
      <span class="toggle-icon">{{ isExpanded ? '▾' : '▸' }}</span>
      <span
        v-if="hasEntries && !isExpanded"
        class="entry-count"
      >
        ({{ entries.length }})
      </span>
    </button>

    <div v-if="showBody" class="trace-body">
      <template v-if="hasEntries">
        <div
          v-for="(entry, i) in entries"
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
            v-if="i < entries.length - 1"
            class="trace-separator"
          />
        </div>
      </template>
      <div v-else class="trace-empty">
        尚无执行记录
      </div>
    </div>
  </div>
</template>

<style scoped>
.trace-panel {
  flex-shrink: 0;
}

.trace-panel.full-height {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  border-top: none;
}

.trace-toggle {
  width: 100%;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-slate);
  background: #fafaf8;
  border: none;
  border-top: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-display);
  transition: background 0.15s;
}

.trace-toggle:hover {
  background: #f5f2ec;
}

.toggle-icon {
  font-size: 10px;
}

.entry-count {
  font-weight: 400;
  color: var(--color-slate-light);
  font-family: var(--font-body);
}

.trace-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  background: #fafaf8;
  font-family: var(--font-display);
  font-size: 14px;
  line-height: 1.9;
  color: var(--color-ink);
}

.trace-panel:not(.full-height) .trace-body {
  max-height: 260px;
  flex: none;
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
  color: var(--color-ink);
  padding: 4px 0;
}

.trace-jing {
  font-weight: 600;
  color: var(--color-ink);
}

.trace-zhu {
  color: var(--color-ink-light);
  padding-left: 8px;
}

.trace-shu {
  color: var(--color-slate);
  padding-left: 8px;
  font-size: 13px;
}

.trace-annotation {
  color: var(--color-slate-light);
  padding-left: 4px;
  font-size: 12px;
}

.trace-separator {
  height: 1px;
  background: var(--color-border-light);
  margin: 6px 0;
}

.trace-empty {
  color: #d1cbc0;
  font-style: italic;
  text-align: center;
  padding: 40px 0;
}
</style>
