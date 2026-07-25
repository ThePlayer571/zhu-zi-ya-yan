<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useProgramStore } from '../stores/program'
import CodeEditor from './CodeEditor.vue'
import RunButton from './RunButton.vue'
import OutputDisplay from './OutputDisplay.vue'
import InputPrompt from './InputPrompt.vue'
import TracePanel from './TracePanel.vue'

const store = useProgramStore()
const activeTab = ref<'io' | 'trace'>('io')

onMounted(() => {
  store.connect()
})

watch(() => store.isAwaitingInput, (val) => {
  if (val) {
    activeTab.value = 'io'
  }
})
</script>

<template>
  <section id="editor-section" class="home-editor">
    <div class="editor-shell">
      <RunButton
        :can-run="store.canRun"
        :is-running="store.isRunning"
        :has-just-finished="store.hasJustFinished"
        @run="store.runProgram()"
        @cancel="store.cancelProgram()"
      />
      <div class="editor-main">
        <!-- 左栏：代码编辑器 -->
        <div class="editor-left">
          <CodeEditor
            :model-value="store.sourceCode"
            :disabled="store.isRunning"
            @update:model-value="store.sourceCode = $event"
          />
        </div>

        <!-- 右栏：选项卡切换 -->
        <div class="editor-right">
          <!-- 选项卡头部 -->
          <div class="tab-header">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'io' }"
              @click="activeTab = 'io'"
            >
              <span class="tab-icon">◇</span>
              <span>交互台</span>
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'trace' }"
              @click="activeTab = 'trace'"
            >
              <span class="tab-icon">◈</span>
              <span>经注疏</span>
              <span
                v-if="store.traceEntries.length > 0"
                class="tab-badge"
              >
                {{ store.traceEntries.length }}
              </span>
            </button>
          </div>

          <!-- 输入输出面板 -->
          <div v-show="activeTab === 'io'" class="tab-panel io-panel">
            <OutputDisplay :lines="store.output" />
            <InputPrompt
              :visible="store.isAwaitingInput"
              :prompt-text="store.inputPrompt"
              @submit="store.provideInput($event)"
            />
          </div>

          <!-- 经注疏面板 -->
          <div v-show="activeTab === 'trace'" class="tab-panel trace-panel-full">
            <TracePanel :entries="store.traceEntries" :always-open="true" />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home-editor {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
  background: linear-gradient(180deg, #ede4cf 0%, #f0e8d5 30%, var(--color-paper) 100%);
}

.editor-shell {
  width: 100%;
  max-width: 1400px;
  height: calc(100vh - 64px);
  max-height: 900px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow:
    0 2px 24px rgba(26, 20, 16, 0.06),
    0 0 0 1px rgba(26, 20, 16, 0.03);
}

.editor-main {
  flex: 1;
  display: flex;
  min-height: 0;
}

.editor-left {
  width: 50%;
  border-right: 1px solid var(--color-border-light);
  min-height: 0;
}

.editor-right {
  width: 50%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* ---- Tab Header ---- */

.tab-header {
  display: flex;
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border-light);
  background: #fafaf8;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-display);
  color: var(--color-slate-light);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--color-slate);
  background: rgba(0, 0, 0, 0.02);
}

.tab-btn.active {
  color: var(--color-ink);
  border-bottom-color: var(--color-vermillion);
}

.tab-icon {
  font-size: 10px;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-body);
  color: #fff;
  background: var(--color-vermillion);
  border-radius: 9px;
}

/* ---- Tab Panels ---- */

.tab-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.io-panel {
  display: flex;
  flex-direction: column;
}

.trace-panel-full {
  overflow: hidden;
}

/* ---- Responsive ---- */

@media (max-width: 900px) {
  .home-editor {
    padding: var(--space-sm);
  }

  .editor-shell {
    height: auto;
    min-height: 100vh;
    max-height: none;
  }

  .editor-main {
    flex-direction: column;
  }

  .editor-left,
  .editor-right {
    width: 100%;
    min-height: 50vh;
  }

  .editor-left {
    border-right: none;
    border-bottom: 1px solid var(--color-border-light);
  }
}
</style>
